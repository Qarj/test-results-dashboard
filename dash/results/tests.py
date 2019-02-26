# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode

from .models import Result

import re
import tempfile

#
# Test Helpers
#

def create_test_result(test_name, app_name, test_passed, run_name, run_server):
    """
    Create a test result with the given `test_name`, `app_name`,
    `test_passed`, `run_name`, `run_server`
    """
    return Result.objects.create(test_name=test_name, app_name=app_name, test_passed=test_passed, run_name=run_name, run_server=run_server)

# https://stackoverflow.com/questions/4995279/including-a-querystring-in-a-django-core-urlresolvers-reverse-call
def my_reverse(viewname, kwargs=None, query_kwargs=None):
    """
    Custom reverse to add a query string after the url
    Example usage:
    url = my_reverse('my_test_url', kwargs={'pk': object.id}, query_kwargs={'next': reverse('home')})
    """
    url = reverse(viewname, kwargs=kwargs)

    if query_kwargs:
        return u'%s?%s' % (url, urlencode(query_kwargs))

    return url

def url_for_log(test_name="Default test name", app_name="DefaultApp", run_name="DefaultRun", run_server="TeamCity", test_passed=False, message='', team_name='DefaultTeam'):
    return my_reverse('results:log', query_kwargs={'test_name': test_name, 'app_name': app_name, 'test_passed': test_passed, 'run_name': run_name, 'run_server': run_server, 'message': message, 'team_name': team_name})

class ResultsIndexViewTests(TestCase):
    def test_index(self):
        """
        Results index page exists
        """
        response = self.client.get(reverse('results:index'))
        self.assertEqual(response.status_code, 200)

class AddTestResultTests(TestCase):
    
    #
    # test helpers
    #
    
    def get_detail_from_response(self, response, debug=False):
            m = re.search(r"test_result_id is (\d+)", response.content.decode('utf-8'))
            test_result_id = m.group(1)
            url = reverse('results:detail', args=(test_result_id,))
            return self._get_url(url, debug)

    def get_detail(self, test_result_id, debug=False):
            url = reverse('results:detail', args=(test_result_id,))
            return self._get_url(url, debug)

    def get_latest(self, run_server='', debug=False):
            if (run_server):
                url = reverse('results:latest', args=(run_server,))
            else:
                url = reverse('results:latest')
            return self._get_url(url, debug)

    def get_run(self, run_name, debug=False):
            url = reverse('results:run', args=(run_name,))
            return self._get_url(url, debug)

    def get_team(self, team_name, debug=False):
            url = reverse('results:team', args=(team_name,))
            return self._get_url(url, debug)

    def get_app(self, app_name, run_server='', debug=False):
            if (run_server):
                url = reverse('results:app', args=(app_name,run_server,))
            else:
                url = reverse('results:app', args=(app_name,))
            return self._get_url(url, debug)

    def _get_url(self, url, debug=False):
            response = self.client.get(url)
            if (debug):
                print('\nDebug URL:', url)
                print(response.content.decode('utf-8'), '\n')
            return response


    def log_result(self, test_name="Default test name", app_name="DefaultApp", run_name="DefaultRun", run_server="TeamCity", test_passed=False, message='', team_name="DefaultTeam", debug=False):
            url = url_for_log(test_name=test_name, app_name=app_name, run_name=run_name, run_server=run_server, test_passed=test_passed, message=message, team_name=team_name)
            response = self.client.get(url)
            self.assertContains(response, 'Test logged ok')

            if (debug):
                print('\nDebug URL:', url)
                print(response.content.decode('utf-8'), '\n')

            m = re.search(r"test_result_id is (\d+)", response.content.decode('utf-8'))
            test_result_id = m.group(1)
            url = reverse('results:detail', args=(test_result_id,))
            return test_result_id

    #https://stackoverflow.com/questions/18299307/django-test-how-to-send-a-http-post-multipart-with-json
    #https://stackoverflow.com/questions/3924117/how-to-use-tempfile-namedtemporaryfile-in-python
    def log_file(self, test_name="Default test name", app_name="DefaultApp", run_name="DefaultRun", name='test.txt', desc="Default File Desc", debug=False):
        url = reverse('results:log_file')
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'Some file content')
            f.flush()
            f.seek(0)
            form = {
                'test_name': test_name,
                'app_name': app_name,
                'run_name': run_name,
                'name': name,
                'desc': desc,
                'document': f,
            }
            response = self.client.post(url, data=form)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'File logged ok')

        if (debug):
            print('\nDebug URL:', url)
            print(response.content.decode('utf-8'), '\n')

        return response

    def get_file(self, test_name='d', app_name='d', run_name='d', name='d', debug=False):
        url = my_reverse('results:get_file',
            query_kwargs={
                    'test_name': test_name,
                    'app_name': app_name,
                    'run_name': run_name,
                    'name': name,
                }
            )
        return self._get_url(url, debug)

    def get_artefact_url(self, response):
        m = re.search(r"Artefact url: ([^<]+)", response.content.decode('utf-8'))
        return m.group(1)

    def number_of_instances(self, response, target):
        return response.content.decode('utf-8').count(target)

    def _assertRegex(self, response, regex):
        self.assertRegex(response.content.decode('utf-8'), regex)

    def _assertNotRegex(self, response, regex):
        self.assertNotRegex(response.content.decode('utf-8'), regex)

    #
    # view all results for run
    #
    
    def test_view_all_results_for_run(self):
        """
        View all results for run
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'run test', 'app_name': 'Apply', 'test_passed': 'TRUE', 'run_name': 'My_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, 'Test logged ok')

        url = my_reverse('results:log', query_kwargs={'test_name': 'another test', 'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'My_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, 'Test logged ok')

        url = reverse('results:run', args=("My_Run",))
        response = self.client.get(url)
        self.assertContains(response, 'run test')
        self.assertContains(response, 'another test')

    #
    # view all runs for app
    #

        # test: one line per run with run name

    def test_view_all_runs_for_app(self):
        """
        View all runs for app - run name is shown
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='test 2', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='test 1', app_name='Search', run_name='Run2', run_server='localhost')
        self.log_result(test_name='test 2', app_name='Search', run_name='Run2', run_server='localhost')
        self.log_result(test_name='test 1', app_name='Search', run_name='Run3', run_server='localhost')
        self.log_result(test_name='test 1', app_name='Details', run_name='Run4', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertEqual(self.number_of_instances(response,">Run1<"), 1)
        self.assertEqual(self.number_of_instances(response,">Run2<"), 1)
        self.assertEqual(self.number_of_instances(response,">Run3<"), 1)
        self.assertNotRegex(response.content.decode('utf-8'), 'Run4')

        # test: run server shown

    def test_view_all_runs_for_app_shows_run_server(self):
        """
        View all runs for app - shows run server
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, 'localhost')

        # test: number of tests in run shown

    def test_view_all_runs_for_app_shows_total_number_of_tests(self):
        """
        View all runs for app - shows total number of tests
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='test 2', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='test 3', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, '3 tests')

        # test: number passed tests in run

    def test_view_all_runs_for_app_shows_number_of_passed_tests(self):
        """
        View all runs for app - shows number of passed tests
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)
        self.log_result(test_name='test 2', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)
        self.log_result(test_name='test 3', app_name='Search', run_name='Run1', run_server='localhost', test_passed=False)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, '2 passed')

        # test: number failed tests in run

    def test_view_all_runs_for_app_shows_number_of_failed_tests(self):
        """
        View all runs for app - shows number of failed tests
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)
        self.log_result(test_name='test 2', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)
        self.log_result(test_name='test 3', app_name='Search', run_name='Run1', run_server='localhost', test_passed=False)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, '1 failed')

        # test: overall status shown

    def test_view_all_runs_for_app_shows_overall_status(self):
        """
        View all runs for app - shows overall status
        """
        self.log_result(test_name='test 1', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)
        self.log_result(test_name='test 2', app_name='Search', run_name='Run1', run_server='localhost', test_passed=True)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, 'pass')

        self.log_result(test_name='test 3', app_name='Search', run_name='Run1', run_server='localhost', test_passed=False)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)
        self.assertContains(response, 'fail')

    #
    # view latest run only for all apps (A) #latest
    #

    def test_view_latest_run_only_for_all_apps(self):
        """
        View latest run only for all apps
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1')            #1
        self.log_result(test_name='Truck', app_name='Search', run_name='Run1')          #2
        self.log_result(test_name='Car', app_name='Search', run_name='Run2')            #3
        self.log_result(test_name='Truck', app_name='Search', run_name='Run2')          #4

        self.log_result(test_name='Chicken', app_name='Details', run_name='Run3')       #5
        self.log_result(test_name='Whale', app_name='Details', run_name='Run4')         #6

        self.log_result(test_name='Telephone', app_name='Apply', run_name='Run5')       #7

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Latest run results for all apps')
        self._assertRegex(response, r'Search[^~]+Run2')
        self._assertRegex(response, r'Details[^~]+Run4')
        self._assertRegex(response, r'Apply[^~]+Run5')
        self.assertNotRegex(response.content.decode('utf-8'), 'Run1')
        self.assertNotRegex(response.content.decode('utf-8'), 'Run3')

        #assert that only 3 lines returned
        self.assertEqual(self.number_of_instances(response,">Apply<"), 1)
        self.assertEqual(self.number_of_instances(response,">Search<"), 1)
        self.assertEqual(self.number_of_instances(response,">Details<"), 1)
        self.assertEqual(self.number_of_instances(response,"~ End Row "), 3)

    def test_latest_results_is_html_css_and_has_link_to_run_result(self):
        """
        Latest results is in html css and has a link to the run result
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1')

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<h2>')
        self.assertContains(response, 'style.css')
        self.assertContains(response, 'Ubuntu')
        self.assertContains(response, 'favicon.ico')
        self.assertContains(response, '<title>Latest results</title>')
        self.assertContains(response, '<a href="/results/run/Run1/" class="normal">Run1</a>')
        self.assertContains(response, '<a href="/results/run/Run1/" name="run_status" class="fail">1 tests, 1 failed</a>')

    def test_latest_results_has_link_to_all_app_results(self):
        """
        Latest results is in html css and has a link to the run result
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1')

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<a href="/results/app/Search/" class="normal">Search</a>')

    def test_latest_results_has_link_to_latest_results_for_run_server(self):
        self.log_result(test_name='Smart', app_name='Look', run_name='RunLink', run_server='jacinta')
        self.assertContains(self.get_latest(), '<a href="/results/latest/jacinta/" class="normal">jacinta</a>')

    def test_latest_results_shows_message_when_no_results(self):
        """
        Latest results shows message when no results
        """

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'No results are available')

    def test_latest_results_shows_number_of_tests_in_green_when_all_passed(self):
        """
        Latest results shows the number of tests in green when all passed
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', test_passed=True)
        self.log_result(test_name='Bat', app_name='Search', run_name='Run1', test_passed=True)

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '2 tests')
        self.assertContains(response, 'name="run_status" class="pass"')

    def test_latest_results_shows_number_of_tests_in_red_when_failure_exists(self):
        """
        Latest results shows the number of tests in red when failure exists
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', test_passed=False)
        self.log_result(test_name='Bat', app_name='Search', run_name='Run1', test_passed=True)

        url = reverse('results:latest')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '2 tests, 1 failed')
        self.assertContains(response, 'name="run_status" class="fail"')

    def test_slash_results_also_shows_latest_results(self):
        """
        Latest results shows on just /results/ too
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', test_passed=False)

        url = reverse('results:index')
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Latest results')

    def test_latest_shows_duration_to_zero_dp_seconds(self):
        self.log_result(test_name='Car', app_name='Search', run_name='RunNow', test_passed='pend')
        self.log_result(test_name='Car', app_name='Search', run_name='RunNow', test_passed=True)

        self.assertContains(self.get_latest(), 'Duration')
        self._assertRegex(self.get_latest(), r'hires_duration=[^>]+>\s*\d+:\d+:\d{2}\s*<')

    #
    # view latest run only for all Apps where run_server = specified (B) #latest/TeamCity
    #

    def test_view_latest_run_only_for_all_apps_for_given_run_server(self):
        """
        View latest run only for all Apps for given run server
        """
        self.log_result(test_name='Car1', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='Car2', app_name='Search', run_name='Run1')
        self.log_result(test_name='Truck1', app_name='Search', run_name='Run1')
        self.log_result(test_name='Car3', app_name='Search', run_name='Run2')
        self.log_result(test_name='Truck3', app_name='Search', run_name='Run2')
        self.log_result(test_name='Truck4', app_name='Search', run_name='Run2', run_server='localhost')

        self.log_result(test_name='Chicken', app_name='Details', run_name='Run3')
        self.log_result(test_name='Whale1', app_name='Details', run_name='Run4', run_server='localhost')
        self.log_result(test_name='Whale2', app_name='Details', run_name='Run4')
        self.log_result(test_name='Whale', app_name='Details', run_name='Run5', run_server='localhost')

        self.log_result(test_name='Telephone1', app_name='Apply', run_name='Run5')
        self.log_result(test_name='Telephone2', app_name='Apply', run_name='Run5', run_server='localhost')
        self.log_result(test_name='Telephone', app_name='Apply', run_name='Run6', run_server='localhost')

        url = reverse('results:latest', args=("TeamCity",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Latest TeamCity run results for all apps')
        self._assertRegex(response, r'Search[^~]+Run2')
        self._assertRegex(response, r'Details[^~]+Run4')
        self._assertRegex(response, r'Apply[^~]+Run5')
        self.assertNotRegex(response.content.decode('utf-8'), 'Run1')
        self.assertNotRegex(response.content.decode('utf-8'), 'Run3')

        #assert that only 3 lines returned
        self.assertEqual(self.number_of_instances(response,">Apply<"), 1)
        self.assertEqual(self.number_of_instances(response,">Search<"), 1)
        self.assertEqual(self.number_of_instances(response,">Details<"), 1)
        
        self.assertContains(response, '<title>Latest results - TeamCity</title>')

    #
    # Individual run result page #run
    #

    def test_individual_run_result_shows_run_name_and_app_name_in_title_and_h2(self):
        """
        Individual run result title shows run_name - app_name in title and h2
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<title>Run1 - Search</title>')
        self.assertContains(response, '<h2>Results for run Run1 - Search')

    def test_individual_run_result_shows_run_server_in_h2(self):
        """
        Individual run result title shows run_server in h2
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='TeamCity')

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Run1 - Search [TeamCity]</h2>')

    def test_individual_run_result_shows_date_and_time_test_run(self):
        """
        Individual run result title shows date and time test was run
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='TeamCity')

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self._assertRegex(response, r'\d+ \w{3,} \d{4}') # April 18, 2018
        self._assertRegex(response, r'\d+:\d+:\d{2}.\d{4,}') # 15:11:05

    def test_individual_run_result_shows_pass_or_fail_status(self):
        """
        Individual run result shows pass or fail status
        """
        self.log_result(test_name='Chicken', app_name='Search', run_name='Run1', test_passed=True)
        self.log_result(test_name='Whale', app_name='Search', run_name='Run1', test_passed=False)

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self._assertRegex(response, r'pass[^~]+Chicken')
        self._assertRegex(response, r'fail[^~]+Whale')

    def test_clicking_pass_fail_result_links_to_result_id_page(self):
        """
        Clicking pass fail result links to result id page
        """
        test_result_id = self.log_result(test_name='Chicken', app_name='Search', run_name='Run1', test_passed=True)

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<a href="/results/' + test_result_id + '/" class="pass">pass</a>')

    def test_individual_run_result_h3_shows_total_test_count_passed_and_failed_in_status_colour(self):
        """
        Individual run result h3 shows count of total tests, number passed, number failed in status colour
        """
        test_result_id = self.log_result(test_name='Chicken', app_name='Search', run_name='Run1', test_passed=True)
        test_result_id = self.log_result(test_name='Whale', app_name='Search', run_name='Run1', test_passed=False)

        url = reverse('results:run', args=("Run1",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<h4 class="fail">2 tests: 1 passed, 1 failed</h4>')

    def test_individual_run_result_has_message_when_no_results_available_and_link_to_latest_results(self):
        """
        All runs for app has message when no results available and link to latest results
        """

        url = reverse('results:run', args=("NoRun",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'No results are available')
        self.assertContains(response, '/results/latest/')

    def test_individual_run_result_shows_start_and_end_column_headings(self):
        self.log_result(test_name='Jellyfish', app_name='Search', run_name='Run1', test_passed=True)
        self.assertContains(self.get_run('Run1'), '<th>Start</th>')
        self.assertContains(self.get_run('Run1'), '<th>End</th>')
        self.assertContains(self.get_run('Run1'), 'td name="start"')
        self.assertContains(self.get_run('Run1'), 'td name="end"')
        
    def test_individual_run_result_shows_duration(self):
        self.log_result(test_name='Frog', app_name='Search', run_name='Run1', test_passed=False)
        self.log_result(test_name='Frog', app_name='Search', run_name='Run1', test_passed=True)
        self._assertRegex(self.get_run('Run1'), r'td name="duration"[^>]*>\s*\d+:\d+')

    def test_individual_run_result_does_not_show_duration_or_end_for_pending_result(self):
        self.log_result(test_name='Frog', app_name='Search', run_name='Run1', test_passed='pend')
        self._assertNotRegex(self.get_run('Run1'), r'td name="duration">\s*\d+:\d+')
        self._assertNotRegex(self.get_run('Run1'), r'td name="end">\s*\d+ \w+')

    def test_individual_run_result_shows_message(self):
        self.log_result(test_name='Rabbit', app_name='Offer', run_name='RunX', test_passed='fail', message='It errored out')
        self.assertContains(self.get_run('RunX'), 'It errored out')

    #
    # All runs for app page #app
    #

    def test_all_runs_for_app_shows_app_name_in_title_and_h2(self):
        """
        All runs for app shows app_name in title and h2
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<title>Search</title>')
        self.assertContains(response, '<h2>All results for Search')

    def test_all_runs_for_app_shows_run_name_and_run_server_columns(self):
        """
        All runs for app shows run_name - and run_server
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Run1')
        self.assertContains(response, 'localhost')

    def test_all_runs_for_app_shows_start_time_for_each_run_with_heading(self):
        """
        All runs for app shows start time for each run
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self._assertRegex(response, r'\d+ \w{3,} \d{4}')
        self._assertRegex(response, r'\d+:\d+:\d{2}.\d{4,}')
        self.assertContains(self.get_app('Search'), '<th>Start</th>')

    def test_all_runs_for_app_shows_number_of_tests_and_total_passed_and_total_failed_for_each_run(self):
        """
        All runs for app shows number of tests with total passed and total failed for each run row
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', test_passed=False)
        self.log_result(test_name='Hat', app_name='Search', run_name='Run1', test_passed=True)
        self.log_result(test_name='Lat', app_name='Search', run_name='Run1', test_passed=False)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '3 tests')
        self.assertContains(response, '1 passed')
        self.assertContains(response, '2 failed')
        self.assertContains(response, 'name="run_status" class="fail"')

    def test_all_runs_for_app_shows_number_of_runs_with_total_passed_runs_and_total_failed_runs(self):
        """
        All runs for app shows total number of runs + total passed runs + total failed runs in h4 in normal colour (not status)
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', test_passed=False)
        self.log_result(test_name='Hat', app_name='Search', run_name='Run1', test_passed=True)
        self.log_result(test_name='Car', app_name='Search', run_name='Run2', test_passed=True)
        self.log_result(test_name='Hat', app_name='Search', run_name='Run2', test_passed=True)

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<h4>2 test runs: 1 passed, 1 failed')

    def test_all_runs_for_app_shows_end_time_for_each_run_with_heading(self):
        """
        All runs for app shows end time for each run
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='Hat', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(self.get_app('Search'), '<th>End</th>')

    def test_all_runs_for_app_shows_run_duration(self):
        self.log_result(test_name='Tram', app_name='Search', run_name='Run1', run_server='localhost')
        self.log_result(test_name='Tube', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Run duration')
        self._assertRegex(response, r'0:00:00')

    def test_all_runs_for_app_has_link_for_run_name_and_run_status(self):
        """
        All runs for app has link for run name
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<a href="/results/run/Run1/" class="normal">Run1</a>')
        self.assertContains(response, '<a href="/results/run/Run1/" name="run_status" class="fail">1 tests: 1 failed</a>')

    def test_all_runs_for_app_has_message_when_no_results_available_and_link_to_latest_results(self):
        """
        All runs for app has message when no results available and link to latest results
        """

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'No results are available')
        self.assertContains(response, '/results/latest/')

    def test_all_runs_for_app_links_to_latest_results_for_that_run_server(self):
        """
        All runs for app links to latest results for that run_server
        """
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost')

        url = reverse('results:app', args=("Search",))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<a href="/results/app/Search/localhost/" class="normal">localhost</a>')

    def test_0_pending_and_0_failed_do_not_show_for_run_summary(self):
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost', test_passed='pass')
        self.assertContains(self.get_app('Search'), '>1 tests: 1 passed<')

    def test_0_pending_and_0_failed_do_not_show_for_all_runs_summary(self):
        self.log_result(test_name='Car', app_name='Search', run_name='Run1', run_server='localhost', test_passed='pass')
        self.assertContains(self.get_app('Search'), '>1 test runs: 1 passed<')

    def test_can_filter_app_results_by_run_server(self):
        self.log_result(test_name='Mad', app_name='Home', run_name='Run1', run_server='localhost', test_passed='fail')
        self.log_result(test_name='Bad', app_name='Home', run_name='Run1', run_server='jacinta', test_passed='pass')
        self.log_result(test_name='Sad', app_name='Home', run_name='Run1', run_server='TeamCity', test_passed='pend')

        response = self.get_app('Home', run_server='jacinta')
        self.assertContains(response, '1 passed')
        self._assertNotRegex(response, 'localhost')
        self._assertNotRegex(response, 'TeamCity')
        self.assertContains(response, 'All results for Home - jacinta')

    def test_app_current_status_is_determined_by_latest_run_result(self):
        self.log_result(test_name='Mad', app_name='Home', run_name='Run1', run_server='TeamCity', test_passed='pend')
        self.assertContains(self.get_app('Home'), 'App status: pend')

        self.log_result(test_name='Bad', app_name='Home', run_name='Run2', run_server='TeamCity', test_passed='fail')
        self.assertContains(self.get_app('Home'), 'App status: fail')

        self.log_result(test_name='Sad', app_name='Home', run_name='Run3', run_server='TeamCity', test_passed='pass')
        self.assertContains(self.get_app('Home'), 'App status: pass')

    #
    # Individual result page #detail
    #

    def test_individual_result_page_shows_table_with_row_for_each_app_name_test_name_test_passed_run_name_run_server_date_created_message(self):
        """
        Individual result shows table with row for each field - app_name, test_name, test_passed, run_name, run_server, date_created, message
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity', message='Hey, Bob!')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, '>Details<')
        self.assertContains(response, '>My really nice test<')
        self.assertContains(response, '>fail<')
        self.assertContains(response, '>DetailsTestRun<')
        self.assertContains(response, '>TeamCity<')
        self._assertRegex(response, r'\d+ \w{3,} \d{4}')
        self._assertRegex(response, r'\d+:\d+:\d{2}.\d{4,}')
        self.assertContains(response, '>Hey, Bob!<')

    def test_individual_result_shows_message_when_no_result_id_exists_and_link_to_latest_results(self):
        """
        Individual result page shows message when no result id exists and link to latest results
        """
        url = reverse('results:detail', args=("555111",))
        response = self.client.get(url)

        self.assertContains(response, 'No results are available')
        self.assertContains(response, '/results/latest/')

    def test_individual_result_page_shows_pass_fail_in_colour(self):
        """
        Individual result shows pass or fail in approriate colour
        """
        test_result_id = self.log_result(test_name='My really nice test for you', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, 'class="boldfail"')

        test_result_id = self.log_result(test_name='My really nice test for them', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity', test_passed=True)

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, 'class="boldpass"')

    def test_individual_result_run_name_links_to_all_results_for_run_name(self):
        """
        Individual result run_name links to all results for run_name
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, '/results/run/DetailsTestRun/')

    def test_individual_result_app_name_links_to_all_results_for_app_name(self):
        """
        Individual result app_name links to all results for app_name
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, '/results/app/Details/')

    def test_individual_result_run_server_links_to_latest_results_for_run_server(self):
        """
        Individual result run_server links to latest results for run_server
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, '/results/latest/TeamCity/')

    def test_individual_result_has_title_and_heading_result_id_1(self):
        """
        Individual result has title and heading Result id 1
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)

        self.assertContains(response, '<title>Result id 1</title>')
        self.assertContains(response, '<h2>Result id 1</h2>')

    def test_individual_result_shows_duration(self):
        id = self.log_result(test_name='Beaut test', app_name='Details', run_name='Run_abc', run_server='TeamCity', test_passed='pend')
        id = self.log_result(test_name='Beaut test', app_name='Details', run_name='Run_abc', run_server='TeamCity', test_passed='fail')
        self.assertContains(self.get_detail(id), '>Duration<')
        self._assertRegex(self.get_detail(id), r'>\d+:\d+:\d+\.?\d+<')

    def test_individual_result_shows_team_name(self):
        id = self.log_result(test_name='Team test', app_name='Details', run_name='Run_abc', run_server='TeamCity', test_passed='pend', team_name='CoolTeam')
        self.assertContains(self.get_detail(id), '>Team Name<')
        self.assertContains(self.get_detail(id), 'CoolTeam')

    def test_do_not_show_end_and_duration_for_pending_result(self):
        id = self.log_result(test_name='Beaut test', app_name='Details', run_name='Run_abc', run_server='TeamCity', test_passed='pend')
        self._assertRegex(self.get_detail(id), r'<td>End[^~]+><')
        self._assertRegex(self.get_detail(id), r'<td>Duration[^~]+><')

    #
    # Delete single result id page #delete
    #

    def test_delete_result_for_id(self):
        """
        Delete result for id
        """
        test_result_id = self.log_result(test_name='delete test 1', app_name='Details', run_name='DeleteTest', run_server='localhost')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)
        self.assertContains(response, 'delete test 1')
        #print (response.content.decode('utf-8'))

        url = reverse('results:delete', args=(test_result_id,))
        response = self.client.get(url)
        self.assertContains(response, 'deleted ok')

        url = reverse('results:detail', args=(test_result_id,))
        response = self.client.get(url)
        self.assertNotRegex(response.content.decode('utf-8'), 'delete test 1')

    def test_delete_result_has_title_and_heading_result_id_1(self):
        """
        Delete result has title and heading Result id 1
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:delete', args=(test_result_id,))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<title>Delete id 1</title>')
        self.assertContains(response, '<h2>Result id 1 deleted ok</h2>')
        self.assertNotContains(response, 'test artefacts were also deleted')

    def test_delete_result_removes_uploaded_files_also(self):
        test_result_id = self.log_result(test_name='My test with files', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        result = self.log_file(test_name='My test with files', app_name='Details', run_name='DetailsTestRun', name='test.test', desc='read file content', debug=False)
        artefact_url = self.get_artefact_url(result)
        result = self._get_url(artefact_url)
        self.assertContains(result, 'Some file content')

        result = self.log_file(test_name='My test with files', app_name='Details', run_name='DetailsTestRun', name='other_file.test', desc='something else', debug=False)

        url = reverse('results:delete', args=(test_result_id,))
        result = self._get_url(url, debug=False)
        self.assertContains(result, '2 test artefacts were also deleted')

        result = self._get_url(artefact_url, debug=False)
        self.assertContains(result, 'File does not exist')

    #
    # Delete old runs - only keep newest number #oldest
    #

    def test_delete_oldest_runs_per_app_only_keep_newest(self):
        """
        Delete oldest runs - only keep newest
        """
        #Example: http://127.0.0.1:8000/results/delete_oldest_runs_per_app_only_keep_newest/50/
        self.log_result(test_name='Car', app_name='PleaseDeleteMe', run_name='Run1')            #1
        self.log_result(test_name='Truck', app_name='PleaseDeleteMe', run_name='Run1')          #2
        self.log_result(test_name='Bike', app_name='PleaseDeleteMe', run_name='Run2')           #3
        self.log_result(test_name='Bicycle', app_name='PleaseDeleteMe', run_name='Run2')        #4
        self.log_result(test_name='Tricycle', app_name='PleaseDeleteMe', run_name='Run3')       #5
        self.log_result(test_name='Plane', app_name='PleaseDeleteMe', run_name='Run3')          #6

        self.log_result(test_name='Chicken', app_name='DeleteMeToo', run_name='Run1')           #7
        self.log_result(test_name='Whale', app_name='DeleteMeToo', run_name='Run2')             #8

        self.log_result(test_name='Telephone', app_name='DeleteMeAlso', run_name='Run1')        #9

        ## Keep 4 runs - this shouldn't delete anything - only at most 3 Runs 
        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(5,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted oldest runs per app ok')
        #
        response = self.get_run('Run1')
        self.assertContains(response, 'Car')
        self.assertContains(response, 'Truck')
        self.assertContains(response, 'Chicken')
        self.assertContains(response, 'Telephone')
        #
        response = self.get_run('Run2')
        self.assertContains(response, 'Bike')
        self.assertContains(response, 'Bicycle')
        self.assertContains(response, 'Whale')
        #
        response = self.get_run('Run3')
        self.assertContains(response, 'Tricycle')
        self.assertContains(response, 'Plane')

        ## Keep 3 runs - this also shouldn't delete anything - only at most 3 Runs 
        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(3,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted oldest runs per app ok')
        #
        response = self.get_run('Run1')
        self.assertContains(response, 'Car')
        self.assertContains(response, 'Truck')
        self.assertContains(response, 'Chicken')
        self.assertContains(response, 'Telephone')
        #
        response = self.get_run('Run2')
        self.assertContains(response, 'Bike')
        self.assertContains(response, 'Bicycle')
        self.assertContains(response, 'Whale')
        #
        response = self.get_run('Run3')
        self.assertContains(response, 'Tricycle')
        self.assertContains(response, 'Plane')

        ## Keep 2 runs - will only remove Run 1 from PleaseDeleteMe app
        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(2,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted oldest runs per app ok')
        #
        response = self.get_run('Run1')
        self.assertNotRegex(response.content.decode('utf-8'), 'Car')
        self.assertNotRegex(response.content.decode('utf-8'), 'Truck')
        self.assertContains(response, 'Chicken')
        self.assertContains(response, 'Telephone')
        #
        response = self.get_run('Run2')
        self.assertContains(response, 'Bike')
        self.assertContains(response, 'Bicycle')
        self.assertContains(response, 'Whale')
        #
        response = self.get_run('Run3')
        self.assertContains(response, 'Tricycle')
        self.assertContains(response, 'Plane')

        ## Keep 1 runs - only latest run kept for each app
        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(1,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted oldest runs per app ok')
        #
        response = self.get_run('Run1')
        self.assertNotRegex(response.content.decode('utf-8'), 'Chicken')
        self.assertContains(response, 'Telephone')
        #
        response = self.get_run('Run2')
        self.assertNotRegex(response.content.decode('utf-8'), 'Bike')
        self.assertNotRegex(response.content.decode('utf-8'), 'Bicycle')
        self.assertContains(response, 'Whale')
        #
        response = self.get_run('Run3')
        self.assertContains(response, 'Tricycle')
        self.assertContains(response, 'Plane')

        ## Keep 0 runs
        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(0,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted oldest runs per app ok')

        response = self.get_run('Run1')
        self.assertNotRegex(response.content.decode('utf-8'), 'Telephone')

        response = self.get_run('Run2')
        self.assertNotRegex(response.content.decode('utf-8'), 'Whale')

        response = self.get_run('Run3')
        self.assertNotRegex(response.content.decode('utf-8'), 'Tricycle')
        self.assertNotRegex(response.content.decode('utf-8'), 'Plane')

    def test_delete_oldest_runs_has_title_and_heading_result_id_1(self):
        """
        Delete oldest runs has title and heading result id
        """
        test_result_id = self.log_result(test_name='My really nice test', app_name='Details', run_name='DetailsTestRun', run_server='TeamCity')

        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(1,))
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<title>Delete oldest</title>')
        self.assertContains(response, '<h2>Deleted oldest runs per app ok</h2>')

    def test_delete_oldest_runs_shows_number_of_runs_removed(self):
        """
        Delete oldest runs shows number of runs removed
        """
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run1')
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run2')
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run3')
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run4')

        url = reverse('results:delete_oldest_runs_per_app_only_keep_newest', args=(1,))
        response = self.client.get(url)
        self.assertContains(response, 'Deleted 3 runs')

    #
    # Log result #log
    #

    #Example: http://127.0.0.1:8000/results/log?test_name=manual%20test&app_name=Apply&test_passed=True&run_name=Manual_Test&run_server=TeamCity
    
    def test_create_test_result(self):
        """
        Can add a test result to the database and see it
        """
        test_result = create_test_result(test_name='First Test', app_name='Apply', test_passed=True, run_name='My_Run', run_server='TeamCity')
        url = reverse('results:detail', args=(test_result.id,))
        response = self.client.get(url)
        self.assertContains(response, test_result.test_name)

    def test_log_test_result_via_api(self):
        """
        Can log a test result via api (get URL)
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'Test logged ok')
        self.assertContains(response, 'simple test')
        self.assertContains(response, 'Apply')
        self.assertContains(response, '>pass<')
        self.assertContains(response, 'Test_Run')
        self.assertContains(response, 'TeamCity')
        
        # The log view has claimed to have logged the result, now let's read it back from the detail view and prove we have the data
        self.get_detail_from_response(response)
        self.assertContains(response, 'simple test')

    # mandatory fields logged

    def test_name_is_mandatory_when_test_result_is_logged(self):
        """
        Must supply test_name when logging a test result
        """
        url = my_reverse('results:log', query_kwargs={'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, 'Test result not logged')
        self.assertContains(response, 'must supply test_name')

    def test_app_name_is_mandatory_when_test_result_is_logged(self):
        """
        Must supply app_name when logging a test result
        """
        url = my_reverse('results:log', query_kwargs={'random_info': 'irrelevant'})
        response = self.client.get(url)
        self.assertContains(response, 'must supply app_name')

    def test_run_name_is_mandatory_when_test_result_is_logged(self):
        """
        Must supply run_name when logging a test result
        """
        url = my_reverse('results:log', query_kwargs={'random_info': 'irrelevant'})
        response = self.client.get(url)
        self.assertContains(response, 'must supply run_name')

    def test_run_server_is_mandatory_when_test_result_is_logged(self):
        """
        Must supply run_server when logging a test result
        """
        url = my_reverse('results:log', query_kwargs={'random_info': 'irrelevant'})
        response = self.client.get(url)
        self.assertContains(response, 'must supply run_server')

    # date time created is automatically added to test result
    
    def test_date_time_created_is_automatically_added_to_test_result(self):
        """
        Date time created is automatically added to test result (i.e. when the test result was logged)
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, 'Test logged ok')

        response = self.get_detail_from_response(response)
        self._assertRegex(response, r'\d+ \w+ \d{4} \d+:\d+:\d+.\d{6}')

    # test_passed is case insensitive for true / false 

    def test_passed_is_case_insensitive_for_true_false(self):
        """
        Case does not matter for test_passed
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 1', 'app_name': 'Apply', 'test_passed': 'TRUE', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, 'Test logged ok')

        response = self.get_detail_from_response(response)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '>pass<')

    def test_passed_accepts_passed_pass_ok_yes_case_insensitive(self):
        """
        Test passed iterprets multiple keywords e.g. passed, passed, ok, yes and is case insensitive
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 1', 'app_name': 'Apply', 'test_passed': 'paSSed', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pass<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 2', 'app_name': 'Apply', 'test_passed': 'oK', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pass<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 3', 'app_name': 'Apply', 'test_passed': 'PaSS', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pass<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 4', 'app_name': 'Apply', 'test_passed': 'YeS', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pass<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 5', 'app_name': 'Apply', 'test_passed': 'truE', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pass<')

    def test_failed_accepts_failed_fail_no_false_case_insensitive(self):
        """
        Test passed iterprets multiple keywords e.g. passed, passed, ok, yes and is case insensitive
        """
        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 1', 'app_name': 'Apply', 'test_passed': 'Failed', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>fail<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 2', 'app_name': 'Apply', 'test_passed': 'nO', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>fail<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 3', 'app_name': 'Apply', 'test_passed': 'FaiL', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>fail<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'case test 4', 'app_name': 'Apply', 'test_passed': 'FALSE', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        response = self.get_detail_from_response(response)
        self.assertContains(response, '>fail<')

    def test_log_result_shows_title_and_heading(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '<title>Log result</title>')
        self.assertContains(response, '<h2>Test logged ok</h2>')

    def test_log_result_shows_test_status(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'test_passed': 'True', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '>pass<')

    def test_log_result_shows_error_messages_with_stylesheet(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, 'style.css')

    def test_can_log_a_short_message(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'Can log a message', 'app_name': 'Apply', 'run_name': 'Test_Run', 'run_server': 'A', 'message': 'Hello World!'})
        response = self.client.get(url)

        #print (response.content.decode('utf-8'))
        self.assertContains(response, '>Message<')
        self.assertContains(response, '>Can log a message<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'Can log a message', 'app_name': 'Apply', 'run_name': 'Test_Run', 'run_server': 'A', 'message': 'Updated Message :)'})
        response = self.client.get(url)
        self.assertContains(response, '>Updated Message :)<')

    #
    # pending results #pend
    #

    def test_missing_test_passed_logged_as_pend(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'simple test', 'app_name': 'Apply', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)

        self.assertContains(response, '>pend<')
        self.assertContains(response, 'class="boldpend"')

        response = self.get_detail_from_response(response)
        self.assertContains(response, '>pend<')
        self.assertContains(response, 'class="boldpend"')

        url = reverse('results:app', args=("Apply",))
        response = self.client.get(url)
        self.assertContains(response, '1 pending')
        self.assertContains(response, 'class="pend"')

        url = reverse('results:run', args=("Test_Run",))
        response = self.client.get(url)
        self.assertContains(response, '1 pending')
        self.assertContains(response, 'class="pend"')

        url = reverse('results:latest')
        response = self.client.get(url)
        #print (response.content.decode('utf-8'))
        self.assertContains(response, '1 pending')
        self.assertContains(response, 'class="pend"')
    
    def test_explicted_test_passed_of_pending_means_pending(self):
        url = my_reverse('results:log', query_kwargs={'test_name': 'cool test 1', 'app_name': 'Apply', 'test_passed': 'penD', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, '>pend<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'cool test 2', 'app_name': 'Apply', 'test_passed': 'pendING', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, '>pend<')

        url = my_reverse('results:log', query_kwargs={'test_name': 'cool test 3', 'app_name': 'Apply', 'test_passed': 'started', 'run_name': 'Test_Run', 'run_server': 'TeamCity'})
        response = self.client.get(url)
        self.assertContains(response, '>pend<')

    def test_passed_failed_pending_at_same_time_latest(self):
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run1', test_passed='pass')
        self.assertContains(self.get_latest(), '>1 tests<')
        self.assertContains(self.get_run('Run1'), '>1 tests: 1 passed<')

        test_result_id = self.log_result(test_name='Test2', app_name='Details', run_name='Run1', test_passed='pend')
        self.assertContains(self.get_latest(), '>2 tests, 1 pending<')
        self.assertContains(self.get_run('Run1'), '>2 tests: 1 passed, 1 pending<')

        test_result_id = self.log_result(test_name='Test3', app_name='Details', run_name='Run1', test_passed='fail')
        self.assertContains(self.get_latest(), '>3 tests, 1 pending, 1 failed<')
        self.assertContains(self.get_run('Run1'), '>3 tests: 1 passed, 1 failed, 1 pending<')

    def test_failed_wins_over_pending_wins_over_passed_for_results_summary_on_latest_run_and_app(self):
        test_result_id = self.log_result(test_name='Test1', app_name='Details', run_name='Run1', test_passed='pass')
        self.assertContains(self.get_latest(), 'name="run_status" class="pass"')
        self.assertContains(self.get_run('Run1'), 'h4 class="pass"')
        self.assertContains(self.get_app('Details'), 'name="run_status" class="pass"')

        test_result_id = self.log_result(test_name='Test2', app_name='Details', run_name='Run1', test_passed='pend')
        self.assertContains(self.get_latest(), 'name="run_status" class="pend"')
        self.assertContains(self.get_run('Run1'), 'h4 class="pend"')
        self.assertContains(self.get_app('Details'), 'name="run_status" class="pend"')

        test_result_id = self.log_result(test_name='Test3', app_name='Details', run_name='Run1', test_passed='fail')
        self.assertContains(self.get_latest(), 'name="run_status" class="fail"')
        self.assertContains(self.get_run('Run1'), 'h4 class="fail"')
        self.assertContains(self.get_app('Details'), 'name="run_status" class="fail"')

    #
    # can update existing result from pending to passed or failed
    #
    
    def test_can_update_test_result_from_pend_to_pass(self):
        test_result_id_1 = self.log_result(test_name='Amaze check', app_name='Details', run_name='Run1', test_passed='pend')
        test_result_id_2 = self.log_result(test_name='Amaze check', app_name='Details', run_name='Run1', test_passed='pass')
        self.assertTrue(test_result_id_1 == test_result_id_2)

        url = reverse('results:detail', args=(test_result_id_1,))
        response = self.client.get(url)
        self.assertContains(response, '>pass<')

    def test_result_update_does_not_change_date_created(self):
        test_result_id_1 = self.log_result(test_name='Super check', app_name='Details', run_name='Run1', test_passed='pend')
        detail_before = self.get_detail(test_result_id_1)
        #print(detail_before.content.decode('utf-8'))

        m = re.search(r"<td>Start[^~]+bold.>([^<]+)", detail_before.content.decode('utf-8'))
        original_date_created = m.group(1)
        #print('Original date created', original_date_created)

        test_result_id_2 = self.log_result(test_name='Super check', app_name='Details', run_name='Run1', test_passed='pass')
        detail_after = self.get_detail(test_result_id_2)
        #print(detail_after.content.decode('utf-8'))

        m = re.search(r"<td>Start[^~]+bold.>([^<]+)", detail_after.content.decode('utf-8'))
        updated_date_created = m.group(1)
        #print('Updated date created', updated_date_created)

        self.assertTrue(len(updated_date_created) > 0)
        self.assertTrue(updated_date_created == original_date_created)

    def test_result_update_auto_updates_date_modified(self):
        test_result_id_1 = self.log_result(test_name='Modified check', app_name='Details', run_name='Run1', test_passed='pend')
        detail_before = self.get_detail(test_result_id_1)
        #print(detail_before.content.decode('utf-8'))

        m = re.search(r"End Date[^~]+bold.>([^<]+)", detail_before.content.decode('utf-8'))
        self._assertRegex(detail_before, r"<td>End[^~]+bold.><")
        original_date_modified = ''

        test_result_id_2 = self.log_result(test_name='Modified check', app_name='Details', run_name='Run1', test_passed='fail')
        detail_after = self.get_detail(test_result_id_2)
        
        m = re.search(r"<td>End[^~]+bold.>([^<]+)", detail_after.content.decode('utf-8'))
        updated_date_modified = m.group(1)
        self.assertTrue(len(updated_date_modified) > 0)
        self.assertTrue(updated_date_modified != original_date_modified)
        #print(updated_date_modified, original_date_modified)
        

        #
        # Log files and read back file directly
        #

    def test_can_log_simple_txt_file(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestRunName', name='test.test', desc='unit test file upload', debug=False)
        self.assertContains(result, 'File logged ok')
        self.assertContains(result, 'Artefact url: /results/get_file/?test_name=UnitTestName&app_name=UnitTestApp&run_name=UnitTestRunName&name=test.test')
        self.assertContains(result, 'File desc: unit test file upload')
        self.assertContains(result, 'File content: Some file content')

    def test_can_read_logged_file_content(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.test', desc='read file content', debug=False)
        artefact_url = self.get_artefact_url(result)
        result = self._get_url(artefact_url)
        self.assertContains(result, 'Some file content')
        self.assertRegex(result['content-type'], 'text/plain')
        result = self.get_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.test', debug=False)
        self.assertContains(result, 'Some file content')
        self.assertRegex(result['content-type'], 'text/plain')

    def test_can_serve_image_jpeg_mime_type(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.jpg', desc='read file content', debug=False)
        result = self.get_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.jpg', debug=False)
        self.assertRegex(result['content-type'], 'image/jpeg')

    def test_can_serve_html_mime_type(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.html', desc='read file content', debug=False)
        result = self.get_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.html', debug=False)
        self.assertRegex(result['content-type'], 'text/html')

    def test_can_serve_image_png_mime_type(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.pNg', desc='read file content', debug=False)
        result = self.get_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.pNg', debug=False)
        self.assertRegex(result['content-type'], 'image/png')

    def test_can_serve_json_mime_type(self):
        result = self.log_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.JsoN', desc='read file content', debug=False)
        result = self.get_file(test_name='UnitTestName', app_name='UnitTestApp', run_name='UnitTestName', name='test.JsoN', debug=False)
        self.assertRegex(result['content-type'], 'application/json')

    def test_can_log_same_file_twice(self):
        result = self.log_file(test_name='UnitTestName1', app_name='UnitTestApp', run_name='UnitTestRunName', name='test.test', desc='unit test file upload', debug=False)
        self.assertContains(result, 'File logged ok')
        result = self.log_file(test_name='UnitTestName1', app_name='UnitTestApp', run_name='UnitTestRunName', name='test.test', desc='unit test file upload', debug=False)
        self.assertContains(result, 'File logged ok')
        id = self.log_result(test_name='UnitTestName1', app_name='UnitTestApp', run_name='UnitTestRunName', run_server='TeamCity', test_passed='fail', debug=False)
        self.get_detail(id, debug=False)


        #
        # Files logged to a test are referenced on the details view
        #

    def test_can_see_link_to_html_file_on_details(self):
        self.log_file(test_name='HTML file', app_name='Details', run_name='Run_bcd', name='test.html', desc='html file', debug=False)
        id = self.log_result(test_name='HTML file', app_name='Details', run_name='Run_bcd', run_server='TeamCity', test_passed='fail', debug=False)
        self.assertContains(self.get_detail(id, debug=False), '>test.html</a>')

    def test_can_see_img_src_link_to_jpg_file_on_details(self):
        self.log_file(test_name='JPG file', app_name='Details', run_name='Run_bcd', name='test.jpg', desc='jpg file', debug=False)
        id = self.log_result(test_name='JPG file', app_name='Details', run_name='Run_bcd', run_server='TeamCity', test_passed='fail', debug=False)
        self._assertRegex(self.get_detail(id, debug=False), 'img src="[^"]+test.jpg"')

    def test_files_in_table_on_details(self):
        id = self.log_result(test_name='Table', app_name='Details', run_name='Run_bcd', run_server='TeamCity', test_passed='fail', debug=False)
        self._assertNotRegex(self.get_detail(id, debug=False), 'files_detail')
        self.log_file(test_name='Table', app_name='Details', run_name='Run_bcd', name='test1.html', desc='html file1', debug=False)
        self.log_file(test_name='Table', app_name='Details', run_name='Run_bcd', name='test2.html', desc='html file2', debug=False)
        self.log_file(test_name='Table', app_name='Details', run_name='Run_bcd', name='screen.jpg', desc='screenshot', debug=False)
        result = self.get_detail(id, debug=False)
        self.assertContains(result, 'files_detail')
        self.assertContains(result, 'name="OffsetFromTestStart"')
        self.assertContains(result, 'name="ArtefactDesc"')
        self.assertContains(result, 'name="Artefact"')


        #
        # Team View
        #

    def test_get_team_view_shows_team_name_in_page_heading(self):
        test_result_id = self.log_result(test_name='Team page', app_name='Details', run_name='SuperRun', test_passed='true', team_name='MyTeam')
        self.assertContains(self.get_team('MyTeam'), 'MyTeam status')

		
## MVP+:

## Phase II
    #test: clicking on test name shows all results for that test name
    #test: can log optional field result_artifact in another table with fk - can take stack trace, needs to be POST
    #test: can log multiple test messages
    #test: result_artifact can take screen shot
    #test: delete code takes test_messages into account
    #test: result_artifacts shown on the individual test result

## Phase III
    #test: view latest run only for all Apps  for Tribe where run_server = specified (C)
    #test: Log test result is async - prove by building in delay parm
    #test: View test results does not stop logging of test results - prove by building in delay parm
    #doco: https://ruslanspivak.com/lsbaws-part3/ (looks like great tutorial)
    

## Maybe
    #test: delete results for run
    #test: delete all results older than days

## Notes
    #skipped NUnit tests - the SetUp and TearDown is never called, so we never log them
        
## https://cgoldberg.github.io/python-unittest-tutorial/
