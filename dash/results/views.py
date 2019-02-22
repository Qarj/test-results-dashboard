# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from itertools import chain

from .models import Result
from .models import Artifact
from .forms import ArtifactForm
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

def index(request):
    return latest(request)

def detail(request, result_id):
    try:
        result = Result.objects.get(pk=result_id)
    except Result.DoesNotExist:
        result = None

    page_title = 'Result id ' + str(result_id)
    page_heading = page_title
    if (result):
        result.test_status = _get_test_status(result.test_passed)
        result.duration = result.date_modified - result.date_created
        if (result.test_status == 'pend'):
            result.date_modified = ''
            result.duration = ''

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'result': result,
    }

    return render(request, 'results/detail.html', context)

def log(request):
    result = Result( test_name = request.GET.get('test_name', None) )
    result.app_name = request.GET.get('app_name', None)
    test_passed_text = request.GET.get('test_passed', None)
    result.test_passed = _convert_test_passed_text_to_true_false_or_none_meaning_pend(test_passed_text)
    result.run_name = request.GET.get('run_name', None)
    result.run_server = request.GET.get('run_server', None)
    result.message = request.GET.get('message', None)
    result.team_name = request.GET.get('team_name', None)

    error = returnErrorMessageIfMandatoryFieldNone('test_name', result.test_name)
    error += returnErrorMessageIfMandatoryFieldNone('app_name', result.app_name)
    error += returnErrorMessageIfMandatoryFieldNone('run_name', result.run_name)
    error += returnErrorMessageIfMandatoryFieldNone('run_server', result.run_server)
    if (error):
        return render(request, 'results/log.html', { 'page_title': 'Error', 'error': error })

    priorResultLab = Result.objects.filter(run_name = result.run_name, app_name=result.app_name, test_name=result.test_name)
    if (priorResultLab):
        priorResult = priorResultLab[0]
        priorResult.test_passed = result.test_passed
        priorResult.message = result.message
        priorResult.save()
        result = priorResult
    else:
        result.save(force_insert=True)

    result.test_status = _get_test_status(result.test_passed)
    info = ''
    page_title = 'Log result'
    page_heading = 'Test logged ok'
    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'result': result,
        'info': info,
        'error': error,
    }

    return render(request, 'results/log.html', context)


# https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html
# https://gearheart.io/blog/how-to-upload-files-with-django/
@csrf_exempt
def log_file(request):
    if request.method != 'POST':
        return _log_file_form(request)

    # form = ArtifactForm(request.POST, request.FILES)
    # if form.is_valid():
    #     form.save()

    artifact = Artifact( test_name = request.POST.get('test_name', None) )
    artifact.app_name = request.POST.get('app_name', None)
    artifact.run_name = request.POST.get('run_name', None)
    artifact.name = request.POST.get('name', None)
    artifact.desc = request.POST.get('desc', None)

    error = returnErrorMessageIfMandatoryFieldNone('test_name', artifact.test_name)
    error += returnErrorMessageIfMandatoryFieldNone('app_name', artifact.app_name)
    error += returnErrorMessageIfMandatoryFieldNone('run_name', artifact.run_name)
    error += returnErrorMessageIfMandatoryFieldNone('name', artifact.name)
    error += returnErrorMessageIfMandatoryFieldNone('desc', artifact.desc)
    if (error):
        return render(request, 'results/log_file.html', { 'page_title': 'Error', 'error': error })

    upload = request.FILES['document']
    fs = FileSystemStorage()
    filename = fs.save(f'artifacts/{artifact.app_name}/{artifact.run_name}/{artifact.test_name}/{artifact.name}', upload)
    uploaded_file_url = fs.url(filename)        
    print('uploaded url', uploaded_file_url)

    # this section proves to a unit test that the file was uploaded
    content = ''
    if artifact.name == 'test.test':
        f = request.FILES['document']
        for chunk in f.chunks():
            content = chunk.decode("utf-8")

    artifact.name = uploaded_file_url # this will be full relative path of (potentially) renamed file due to conflict
    artifact.save()

    page_title = 'Log file'
    page_heading = 'File logged ok'
    error = ''
    url = 'http://example.com/test?value=testing123'
    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'url': url,
        'name': artifact.name,
        'desc': artifact.desc,
        'content': content,
        'error': error,
    }
    return render(request, 'results/log_file.html', context)

def _log_file_form(request):
    form = ArtifactForm()
    context = { 
        'page_title': 'Log file',
        'page_heading': 'Upload test artifact',
        'form': form,
    }
    return render(request, 'results/log_file_form.html', context)

def get_file(request):
    stored_file_name = request.GET.get('stored_file_name', None)
    print('Stored file name according to get_file is', stored_file_name)
    with open(stored_file_name, 'rb') as content_file:
         content = content_file.read()
    # fs = FileSystemStorage()
    # f = fs.open(stored_file_name, mode=None)
    # for chunk in f.chunks():
    #     content = chunk.decode("utf-8")
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
    return HttpResponse(content, content_type="image/jpeg")
    # return HttpResponse('Nothing yet')


def _convert_test_passed_text_to_true_false_or_none_meaning_pend(test_passed_text):
    if (test_passed_text == None):
        return None
    if (test_passed_text == ''):
        return None
    test_passed_text = test_passed_text.lower()
    if (test_passed_text == 'true' or
        test_passed_text == 'pass' or
        test_passed_text == 'passed' or
        test_passed_text == 'yes' or
        test_passed_text == 'ok'):
        return True
    if (test_passed_text == 'pend' or
        test_passed_text == 'pending' or
        test_passed_text == 'running' or
        test_passed_text == 'started'):
        return None
    return False

def _get_test_status(test_passed):
    if (test_passed == None):
        return 'pend'
    if (test_passed):
        return 'pass'
    return 'fail'

def returnErrorMessageIfMandatoryFieldNone(field_name, field_value):
    if (field_value):
        return ''
    return 'Test result not logged - must supply ' + field_name + '! '

def run(request, run_name):
    run_results = Result.objects.filter(run_name=run_name)

    for result in run_results:
        result.test_status = _get_test_status(result.test_passed)
        result.duration, result.duration_text = _get_duration(result.date_created, result.date_modified)
        if (result.test_status == 'pend'):
            result.duration = ''
            result.date_modified = ''

    total_tests, total_failed, total_pending = _get_status_for_run(run_results, run_name)
    total_passed = total_tests - total_failed - total_pending

    overall_status = 'pass'
    if (total_pending > 0):
        overall_status = 'pend'
    if (total_failed > 0):
        overall_status = 'fail'

    page_title = run_name

    page_heading = 'Results for run ' + run_name

    summary = summaryBuilder()
    summary.append_non_zero_value(total_passed, 'passed')
    summary.append_non_zero_value(total_failed, 'failed')
    summary.append_non_zero_value(total_pending, 'pending')
    page_summary = str(total_tests) + ' tests: ' + summary.summary

    if (len(run_results)>0):
        page_title += ' - ' + run_results[0].app_name
        page_heading += ' - ' + run_results[0].app_name + ' [' + run_results[0].run_server + ']'

    context = {
        'run_results': run_results,
        'page_title': page_title,
        'page_heading': page_heading,
        'page_summary': page_summary,
        'overall_status' : overall_status,
    }

    return render(request, 'results/run.html', context)

def _get_duration(start, end):
    duration = end - start
    duration_without_microseconds = str(duration).split('.')[0]
    return duration, duration_without_microseconds

class summaryBuilder:

    already_appended_item = False
    summary = ''
    
    def __init__(self):
        self.already_appended_item = False
        self.summary = ''

    def append_non_zero_value(self, value, desc):
        if (value == 0):
            return
        if (self.already_appended_item):
            self.summary += ', ' + str(value) + ' ' + desc
            return 
        else:
            self.already_appended_item = True
            self.summary += str(value) + ' ' + desc
            return

def team(request, team_name):

    page_title = 'tbd'
    page_heading = team_name + ' status'

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
    }

    return render(request, 'results/team.html', context)


def app(request, app_name, run_server=None):

    if (run_server):
        appLab = Result.objects.filter(app_name=app_name, run_server=run_server)
    else:
        appLab = Result.objects.filter(app_name=app_name)

    # First get a list of all apps
    app_run_list = remove_duplicates_from_list_preserving_order(list( appLab.values_list("run_name", flat=True) ) )

    output = ''
    app_results = []
    run_count = 0
    failed_run_count = 0
    pending_run_count = 0
    app_status = 'fail'
    for run_name in app_run_list:
        run_count += 1
        this_run_name = run_name
        runLab = appLab.filter(run_name=run_name)
        firstTestLogDate = runLab[0].date_created.strftime("%a %d/%m/%Y %H:%M:%S") # Wed 18 Mar, 2018 15:11:05
        start = runLab[0].date_created # the first logged test is always the first test started
        end = _get_last_modified_time(runLab) # we need to check every result to find the last completed
        duration, duration_text = _get_duration(start, end)
        runServer = runLab[0].run_server
        this_run_server = runLab[0].run_server
        runTotalTests = len(runLab)
        runPendingTests = sum(r.test_passed == None for r in runLab)
        runPassedTests = sum(r.test_passed == True for r in runLab)
        runFailedTests = sum(r.test_passed == False for r in runLab)
        this_run_status = 'pass'
        if (runPendingTests > 0 and runFailedTests == 0):
            this_run_status = 'pend'
            pending_run_count += 1
        if (runFailedTests > 0):
            this_run_status = 'fail'
            failed_run_count += 1

        summary = summaryBuilder()
        summary.append_non_zero_value(runPassedTests, 'passed')
        summary.append_non_zero_value(runFailedTests, 'failed')
        summary.append_non_zero_value(runPendingTests, 'pending')
        this_run_status_desc = str(runTotalTests) + ' tests: ' + summary.summary

        app_results.append ( {
            'run_name': this_run_name,
            'run_status': this_run_status,
            'run_status_desc': this_run_status_desc,
            'run_server': this_run_server,
            'start': start,
            'end': end,
            'duration_text': duration_text,
        } )
        app_status = this_run_status

    page_title = app_name
    page_heading = 'All results for ' + app_name
    if (run_server):
        page_title += ' - ' + run_server
        page_heading += ' - ' + run_server

    summary = summaryBuilder()
    summary.append_non_zero_value(run_count - failed_run_count - pending_run_count, 'passed')
    summary.append_non_zero_value(failed_run_count, 'failed')
    summary.append_non_zero_value(pending_run_count, 'pending')
    app_status_desc = str(run_count) + ' test runs: ' + summary.summary

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'app_status_desc' : app_status_desc,
        'app_results': app_results,
        'app_name': app_name,
        'app_status': app_status,
    }

    return render(request, 'results/app.html', context)

def _get_last_modified_time(resultLab):
    last_modified = resultLab[0].date_modified
    for result in resultLab:
        if (result.date_modified > last_modified):
            last_modified = result.date_modified
    return last_modified        

def delete(request, result_id):
    Result.objects.filter(id=result_id).delete()
    
    page_title = 'Delete id ' + str(result_id)
    page_heading = 'Result id ' + str(result_id) + ' deleted ok'

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
    }

    return render(request, 'results/delete.html', context)

def remove_duplicates_from_list_preserving_order(list_with_duplicates): 
   seen = {}
   result = []
   for item in list_with_duplicates:
       if item in seen: continue
       seen[item] = 1
       result.append(item)
   return result

def delete_oldest_runs_only_keep_newest(request, number_of_runs_to_keep):
    
    # repeat per app:
    #   get all the run names for an app - order by create date
    #   delete the excess runs
    
    app_list = remove_duplicates_from_list_preserving_order(list( Result.objects.values_list("app_name", flat=True) ) )

    runs_deleted_count = 0
    for app_name in app_list:
        keep_list = remove_duplicates_from_list_preserving_order(list( Result.objects.filter(app_name=app_name)
            .order_by('run_name', 'date_created').values_list("run_name", flat=True) ) )
    
        number_of_runs_to_remove_from_keep_list = len(keep_list) - number_of_runs_to_keep
        if (number_of_runs_to_remove_from_keep_list < 0):
            number_of_runs_to_remove_from_keep_list = 0
    
        remove_list = keep_list[:number_of_runs_to_remove_from_keep_list]

        for run_to_remove in remove_list:
            runs_deleted_count += 1
            Result.objects.filter(run_name=run_to_remove, app_name=app_name).delete()

    page_title = 'Delete oldest'
    page_heading = 'Deleted oldest runs per app ok'

    context = {
        'page_title': page_title,
        'page_heading': page_heading,
        'runs_deleted_count': runs_deleted_count,
    }

    return render(request, 'results/delete_oldest.html', context)

def latest(request, run_server=None):
    resultLab = Result.objects.all()

    # First get a list of all apps
    app_list = remove_duplicates_from_list_preserving_order(list( resultLab.values_list("app_name", flat=True) ) )

    # Then go through the list backwards - latest run will be the first record we come across for each app
    response = ''
    latest_results = []
    for app_name in app_list:
        found = False
        for result in reversed(resultLab):
            if (result.app_name == app_name and _run_server_matches_or_not_specified(result.run_server, run_server)):
                result.run_status = 'pass'
                result.total_tests, result.total_failed, result.total_pending = _get_status_for_run(resultLab, result.run_name)
                result.start, result.end = _get_start_and_end_time_for_run(resultLab, result.run_name, result.date_created)
                result.duration, result.duration_text = _get_duration(result.start, result.end)
                result.failed_message = ''
                if (result.total_pending > 0):
                    result.run_status = 'pend'
                    result.failed_message += ', ' + str(result.total_pending) + ' pending'
                if (result.total_failed > 0):
                    result.run_status = 'fail'
                    result.failed_message += ', ' + str(result.total_failed) + ' failed'
                latest_results.append(result)
                break

    page_heading = 'Latest '
    page_title = 'Latest results'
    if (run_server):
        page_heading += run_server + ' '
        page_title += ' - ' + run_server
    page_heading += 'run results for all apps'

    context = {
        'latest_results': latest_results,
        'page_heading': page_heading,
        'page_title': page_title,
    }

    return render(request, 'results/latest.html', context)

def _run_server_matches_or_not_specified(result_run_server, run_server):
    if (run_server == None):
        return True
    if (result_run_server == run_server):
        return True
    return False

def _get_status_for_run(resultLab, run_name):
    total_tests = 0
    total_failed = 0
    total_pending = 0
    for result in resultLab:
        if (result.run_name == run_name):
            total_tests += 1
            if (result.test_passed == None):
                total_pending += 1
                continue
            if (not result.test_passed):
                total_failed += 1
    return total_tests, total_failed, total_pending

def _get_start_and_end_time_for_run(resultLab, run_name, date_created):
    start = date_created
    end = date_created
    for result in resultLab:
        if (result.run_name == run_name):
            if (result.date_created < start):
                start = result.date_created
            if (result.date_modified > end):
                end = result.date_modified
    return start, end
