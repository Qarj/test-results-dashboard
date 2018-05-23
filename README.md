# test-results-dashboard

POC for test results dashboard

## Setup

### Install dependencies
Windows:
```
pip install Django
```

Linux:
```
cd /
sudo apt-get install python3-pip
sudo apt-get install python3-virtualenv
sudo apt install gnome-terminal
mkdir venv
cd venv
sudo virtualenv dash
. dash/bin/activate
pip3 install Django
cd /var/www
sudo mkdir dash
sudo chmod 777 dash
cd dash
sudo git clone ...
cd test-results-dashboard
python3 linux_new_dashboard.py
```

### Create a dashboard and load some test data
```
cd test-results-dashboard
python new_dashboard_with_test_data_(will_erase_all).py
```

## Start the server
```
cd dash
python manage.py runserver
```

## Run the tests

### Django Unit Tests

```
cd dash
python manage.py test results
```

The server does not need to be running for the unit tests.

### WebInject Tests

Run the WebInject tests from the project root folder.

```
..\webinject-framework\wif.pl ..\test-results-dashboard\tests\start.py.xml
..\webinject-framework\wif.pl ..\test-results-dashboard\tests\delete_dashboard_then_create_empty.py.xml
..\webinject-framework\wif.pl ..\test-results-dashboard\tests\new_dashboard_with_test_data_(will_erase_all).py.xml
..\webinject-framework\wif.pl ..\test-results-dashboard\tests\load_test_data.py.xml
```

## Use the Test Results Dashboard

### Log a test result
http://127.0.0.1:8000/results/log?test_name=manual%20test&app_name=Apply&test_passed=True&run_name=Manual_Test&run_server=TeamCity&message=stack%20overflow

### View a single test result
http://127.0.0.1:8000/results/2

### View all runs for an app
http://127.0.0.1:8000/results/app/Apply
http://127.0.0.1:8000/results/app/Details
http://127.0.0.1:8000/results/app/Search

### View results for a run
http://127.0.0.1:8000/results/run/Demo

### View latest results
http://127.0.0.1:8000/results/latest

### View latest results for a run server
http://127.0.0.1:8000/results/latest/TeamCity

### Delete a single test result
http://127.0.0.1:8000/results/delete/5

### Delete all the runs except for the most recent 50
http://127.0.0.1:8000/results/delete_oldest_runs_only_keep_newest/50/


## Look at the reference

https://docs.djangoproject.com/en/2.0/intro/tutorial01/

