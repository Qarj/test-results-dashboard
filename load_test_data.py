#!/usr/bin/env python3

version="0.1.0"

import urllib.request, urllib.parse, random, string
import requests

final_results = []

def log_test_result(number=1, app="DefaultApp", run_name="DefaultRun", test_passed=True, run_server='TeamCity', message=''):
    test_name = 'acceptance%20test%20' + str(number)
    host = f'http://{host_name}:{port}'
    urllib.request.urlopen(host
        + '/results/log/?test_name=' + test_name
        + "&app_name=" + app
        + "&test_passed=" + str(test_passed)
        + "&run_name=" + run_name
        + "&run_server=" + run_server
        + "&message=" + urllib.parse.quote_plus(message)
        ).read()
    response = requests.post(
        f'{host}/results/log_file/',
        files=_build_mulitpart_form_data('screenshot.png', 'tests/assets/', test_name, app, run_name, 'Screen shot when error occurred')
    )

def _build_mulitpart_form_data(filename, path, test_name, app, run_name, desc):
    return {
        'test_name': (None, test_name),
        'app_name': (None, app),
        'run_name': (None, run_name),
        'name': (None, filename),
        'desc': (None, desc),
        'document': (filename, open(f'{path}{filename}', 'rb')),
    }

def load_data_for(app="DefaultApp", run_name="DefaultRun", random_status=False, run_server='TeamCity'):
    global final_results

    for number in range (1, 16):
        test_passed = 'true'
        if (random_status and random.random() > 0.85):
            test_passed = 'false'
        if (random_status and random.random() > 0.85):
            test_passed = 'pend'

        # we will log the final result afterwards
        final_results.append ( {
            'number': number,
            'app': app,
            'run_name': run_name,
            'test_passed': test_passed,
            'run_server': run_server,
            'message': 'Message for test ' + str(number),
        } )

        # log the initial result as pending
        try:
            log_test_result(number=number, app=app, run_name=run_name, test_passed='pend', run_server=run_server)
        except urllib.error.URLError:
            print ("Could not load test data - is server running?")
            exit()
    print ("Test data loaded ok for " + app + " app, run " + run_name)

            
def get_run():
    rand = ''.join(random.sample(string.ascii_uppercase + string.digits, k=10))
    return 'TestRun_' + rand

host_name = "127.0.0.1"
port = "8811"
path = "/results"

load_data_for(app="Search", run_name='Pass_Demo', random_status=True)
load_data_for(app="Search", run_name='Cool_Demo', random_status=False)
load_data_for(app="Details", run_name=get_run())
load_data_for(app="Details", run_name=get_run(), run_server="jacinta-west")
load_data_for(app="Details", run_name=get_run(), random_status=True)
load_data_for(app="Apply", run_name=get_run(), random_status=True)
load_data_for(app="Apply", run_name=get_run())
load_data_for(app="Apply", run_name=get_run())
load_data_for(app="Apply", run_name=get_run(), run_server="minerva-polaris")
load_data_for(app="Apply", run_name=get_run(), random_status=True)
load_data_for(app="Home", run_name=get_run())
load_data_for(app="Home", run_name=get_run())
load_data_for(app="Personalisation", run_name=get_run(), run_server="minerva-polaris")
load_data_for(app="eCommerce", run_name=get_run(), run_server="jacinta-west")
load_data_for(app="JobManager", run_name=get_run(), run_server="jacinta-west", random_status=True)
load_data_for(app="ResponseManager", run_name=get_run(), run_server="jacinta-west", random_status=True)
load_data_for(app="IJM", run_name=get_run(), run_server="bluebell", random_status=True)
load_data_for(app="Recommender", run_name=get_run(), run_server="bluebell", random_status=True)

# We do this to get a non zero duration for completed tests
for result in final_results:
    if (result['test_passed'] == 'pend'):
        continue
    log_test_result (
        number=result['number'],
        app=result['app'],
        run_name=result['run_name'],
        test_passed=result['test_passed'],
        run_server=result['run_server'],
        message=result['message'],
    )
print ("Set final test results ok")
