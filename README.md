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
sudo apt update
sudo apt-get install python3-pip
sudo apt-get install python3-venv
sudo apt install gnome-terminal
sudo apt install apache2
sudo apt install apache2-dev

cd /usr/local
sudo mkdir venvs
sudo chmod 777 venvs
cd venvs
python3 -m venv dash
cd dash
source bin/activate
pip install Django
pip install mod_wsgi

cd /var/www
sudo mkdir dash
sudo chmod 777 dash
cd dash
sudo git clone https://github.com/Qarj/test-results-dashboard
cd test-results-dashboard
sudo chmod 777 dash
sudo chmod 777 dash/results/migrations
sudo chmod 777 dash/polls/migrations
python linux_new_dashboard.py
```
The last command will perform migrations, open a new gnome-terminal tab, and load a bunch of test data.

Now close the Django development server (new gnome-terminal tab created).

Then back in the same terminal shell with (dash) Python 3 environment activated:
```
mod_wsgi-express module-config | sudo tee /etc/apache2/conf-enabled/wsgi.conf
sudo cp /var/www/dash/test-results-dashboard/dash/httpd-vhosts_linux.conf /etc/apache2/sites-enabled/test-results-dashboard.conf
sudo systemctl restart apache2
verify with url: http://localhost/dash/results
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

