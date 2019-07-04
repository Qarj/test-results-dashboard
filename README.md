# test-results-dashboard

This project is for viewing test results for any test framework that can access HTTP.
It is particularly suited for tests using Selenium, WebDriver or Puppeteer.

First, you deploy this project to a server on the company intranet either on Windows or Linux using Apache. 

Then in the `Before` hook you call the dashboard with a http GET to indicating the current test name and that it is pending.

In the `After` hook you call the dashboard again to indicate `pass` or `fail`.

Optionally you can upload test artefacts like screenshots, DOM or anything you want. Then when you view the test result
you'll see the screenshots and links to the other files uploaded for the test scenario.

Requires Python 3.6 or higher, tested with Python 3.6.5 and 3.7.2.

# Some screenshots with the included test data

## Latest results view
![Alt text](dev/assets/results.png?raw=true "Latest Results")

## All test results for a single run
In this example, some tests have not yet completed. There is no need to wait until all the tests
have finished before seeing some results.
![Alt text](dev/assets/results_run_TestRun.png?raw=true "Run Result")

## Test result for one scenario
If you uploaded a screenshot or two here, and maybe the HTML DOM, then you will see that also.
![Alt text](dev/assets/results_detail.png?raw=true "Individual Test Result")


# API

## Summary

The paths given below are relative to the {SITE_ROOT} location.

For the Django development server, {SITE_ROOT} is http://127.0.0.1:8811/

If you have deployed this to Apache, then the {SITE_ROOT} might be like http://dash.mycompany/dash/

## Log a test result

HTTP GET
```
{SITE_ROOT}results/log?test_name=ApplyAsNewUser&app_name=Apply&test_passed=False&run_name=Apply_Core_J9ZJK&run_server=TeamCity&message=Stack+Trace+...
```

Parameter   | Example Value
----------- | ------------- 
test_name   | ApplyAsNewUser
app_name    | Apply
test_passed | False
run_name    | Apply_Core_J9ZJK
run_server  | TeamCity
message     | Stack+Trace+...

Best practice is to generate a unique run_name every time the tests are kicked off. All test results for that run
will be grouped by that run_name.

## Upload a file for a test result

HTTP POST
```
{SITE_ROOT}results/log_file
```

posttype
```
multipart/form-data
```

postbody
```
{
    test_name: 'ApplyAsNewUser',
    app_name: 'Apply',
    run_name: 'JZ2K9',
    name: 'FinalState.jpg',
    desc: 'Screen shot when error occurred',
    document: file,
}
```

Response fragment
```
    <h2>File logged ok</h2>
    <p>name: FinalState.jpg</p>
    <p>File desc: Screen shot when error occurred</p>
    <p>Artefact url: /results/get_file/?test_name=ApplyAsNewUser&app_name=Apply&run_name=JZ2K9&name=FinalState.jpg</p>
```

## Download file

HTTP GET
```
{SITE_ROOT}results/get_file/?test_name=ApplyAsNewUser&app_name=Apply&run_name=JZ2K9&name=FinalState.jpg
```
The files uploaded for a test result will be automatically visible on the individual test result details.

## View all runs for an app

```
{SITE_ROOT}results/app/Apply
{SITE_ROOT}results/app/Details
{SITE_ROOT}results/app/Search
```

## View results for a run
```
{SITE_ROOT}results/run/Apply_Core_J9ZJK
```

## View latest results
```
{SITE_ROOT}results/latest
```

## View latest results for a run server
```
{SITE_ROOT}results/latest/TeamCity
```

## View a single test result id
```
{SITE_ROOT}results/2
```
Any files logged will be visible here.

## Delete a single test result id

HTTP GET
```
{SITE_ROOT}results/delete/5
```
Any associated files will be removed from the file system also.

## Keep the newest <int> runs for an app, others will be deleted

HTTP GET
```
{SITE_ROOT}results/app/Apply/keep/5
```
Any associated files will be removed from the file system also.

## Delete all the runs except for the most recent <int> per app

HTTP GET
```
{SITE_ROOT}results/delete_oldest_runs_per_app_only_keep_newest/50/
```
Any associated files will be removed from the file system also.


# Linux Apache Deployment

Needs at least Python 3.6. See https://github.com/Qarj/linux-survival/blob/master/BuildPython3.md for details
on building Python from source.

First install required system packages as root:
```
sudo apt update
sudo apt-get --yes install python3-pip
sudo apt-get --yes install python3-venv
sudo apt --yes install gnome-terminal
sudo apt --yes install apache2
sudo apt --yes install apache2-dev
```

Now create a Python 3 virtual environment and activate it:
```
cd /usr/local
sudo mkdir venvs
sudo chmod 777 venvs
cd venvs
python3 -m venv dash
cd dash
source bin/activate
```

Now that the virtual environment is active, any `python` and `pip` commands will
refer to Python 3, and not Python 2. Prove this:
```
python --version
```

Install the necessary packages for test-results-dashboard as a normal user, not as root:
```
pip install Django
pip install mod_wsgi
pip install requests
```
If you are plagued by SSL errors, then you need to build Python 3 manually to sort it out.
Check here for how to do this: https://github.com/Qarj/linux-survival/blob/master/BuildPython3.md
When you've got Python 3 working with shared libraries, `cd /usr/local/venvs` then `rm -r dash` go
back to the `python3 -m venv dash` step and continue from there.

Create a folder for test-results-dashboard and clone the project:
```
cd /var/www
sudo mkdir dash
sudo chmod 777 dash
cd dash
sudo git clone https://github.com/Qarj/test-results-dashboard
```

Set permissions so the Apache user can access the project:
```
cd /var/www/dash/test-results-dashboard
sudo chmod 777 dash
sudo chmod 777 dash/results
```

Initialise the database (or recreate it):
```
cd dev
python delete_dashboard_then_create_empty.py
sudo chmod 666 /var/www/dash/test-results-dashboard/dash/db.sqlite3
sudo rm -r /var/www/dash/test-results-dashboard/dash/artefacts
mkdir /var/www/dash/test-results-dashboard/dash/artefacts
sudo chmod 777 /var/www/dash/test-results-dashboard/dash/artefacts
```

Start the development server
```
python start.py
```

Load some test data
```
python load_test_data.py
cd /var/www/dash/test-results-dashboard/dash/artefacts
sudo find . -type f -exec chmod a+rw {} \;
sudo find . -type d -exec chmod a+rw {} \;
```

Check that the dashboard seems to be working at http://localhost:8811/results/

Now close the Django development server (new gnome-terminal tab or window created).

Then back in the original terminal shell that has the (dash) Python 3 environment activated:
```
cd /var/www/dash/test-results-dashboard
mod_wsgi-express module-config | sudo tee /etc/apache2/conf-enabled/wsgi.conf
sudo cp /var/www/dash/test-results-dashboard/dash/all-qarj-projects-linux.conf /etc/apache2/sites-enabled
sudo rm /etc/apache2/sites-enabled/000-default.conf
sudo systemctl restart apache2
```

Verify with url: http://localhost/dash/results

## Debugging

```
sudo cat /etc/apache2/envvars
sudo cat /var/log/apache2/error.log
```

Optional - deactivate the virtual environment from your shell:
```
deactivate
```

# Windows Apache Deployment
These instructions require 32-bit (not 64 bit!) Python minimum version 3.6.x.

https://www.python.org/downloads/

```
mkdir c:\git
cd /D c:/git
git clone https://github.com/Qarj/test-results-dashboard
pip install Django
pip install requests
```

## Install Apache

From Apache Lounge https://www.apachelounge.com/download/ download Win32 zip file - not 64 bit, then extract so C:\Apache24\bin folder is available.

From Admin terminal (port 80 will need to be free for this to work)
```
C:\Apache24\bin\httpd -k install
C:\Apache24\bin\httpd -k start
```

## Install mod_wsgi-express

Follow instructions exactly, and do not mix 32 and 64 bit!

Microsoft Visual C++ 14.0 build tools are required, you install them from the _Visual Studio Build Tools 2019_
- https://visualstudio.microsoft.com/downloads/ - choose install "Tools for Visual Studio 2019"
- Run the installer, click `Visual C++ build tools` (top left option) then the check box and `MSVC v140 - VS 2015 C++ build tools (v14.00)` on the right hand side
- You might need to reboot

`rc.exe` must be in the system path
- add `C:\Program Files (x86)\Windows Kits\10\bin\10.0.17763.0\x86` to the path

Press Windows Key, type `VS2015` right click `VS2015 x86 Native Tools Command Prompt` then select `Run as administrator`
- Note: On my Windows 7 machine I had to select `Developer Command Prompt for VS 2017 (2)`

If Apache is not installed at a common location, then specify it
```
set "MOD_WSGI_APACHE_ROOTDIR=D:\Apache24"
```

Finally it is possible to install mod_wsgi
```
pip install mod_wsgi
```

## Configure Django to use Apache

```
copy C:\git\test-results-dashboard\dash\all-qarj-projects-windows.conf C:\Apache24\conf\extra\httpd-vhosts.conf
start notepad++ C:\Apache24\conf\httpd.conf
```

Now uncomment the line `Include conf/extra/httpd-vhosts.conf`, then save.

Optional - for localhost testing, add this line to `httpd.conf` to prevent warnings
```
ServerName localhost
```

Keep the file open, there is another change to make.

First
```
mod_wsgi-express module-config
```

then copy the output to httpd.conf after the final `#LoadModule` statement

Now save & close the file.

Restart the Apache server
```
C:\Apache24\bin\httpd -k restart
```

Note 1 - the output from `mod_wsgi-express module-config` will look a bit like
```
LoadFile "c:/python36/python36.dll"
LoadModule wsgi_module "c:/python36/lib/site-packages/mod_wsgi/server/mod_wsgi.cp36-win32.pyd"
WSGIPythonHome "c:/python36"
```

Note 2 - if not running on port 80, then `C:\Apache24\conf\httpd.conf` will need to be changed
to specify the port.
```
<VirtualHost *:8747>
```

## Create a dashboard and load some test data
Initialise the database (or recreate it):
```
cd C:/git/test-results-dashboard/dev
python delete_dashboard_then_create_empty.py
```

Start the development server
```
python start.py
```

Load some test data
```
python load_test_data.py
```
Check that the dashboard seems to be working with the development server http://localhost:8811/results/

Verify Apache deployment with url: http://localhost/dash/results

## Debug
```
start notepad++ /Apache24/conf/extra/httpd-vhosts.conf
start notepad++ /Apache24/logs/error.log
start notepad++ /Apache24/logs/access.log
```    
    
# Development Environment Setup - Windows

This info is only need for further project development.

## Start the Django development server
```
cd dash
python manage.py runserver
```

## Run the test-results-dashboard Django unit tests

```
cd dash
python manage.py test results
```

The server does not need to be running for the unit tests.


# Django reference

https://docs.djangoproject.com/en/2.0/intro/tutorial01/

