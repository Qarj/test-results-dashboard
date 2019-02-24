# test-results-dashboard

See the latest results of acceptance tests per application.

Requires Python 3, tested with Python 3.5.2 and 3.6.5.

# API

## Summary

The paths given below are relative to the {SITE_ROOT} location.

For the Django development server, {SITE_ROOT} is http://127.0.0.1:8000/

If you have deployed this to Apache, then the {SITE_ROOT} might be like http://mydomain.com/dash/

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
    <p>Stored file name: artefacts%2fFinalState_8234jsd.jpg</p>
```

## Download file

HTTP GET
```
{SITE_ROOT}results/get_file/?test_name=ApplyAsNewUser&app_name=Apply&run_name=JZ2K9&name=FinalState.jpg
```
The files uploaded for a test result will be automatically visible on the individual test details page,
e.g. `{SITE_ROOT}results/2` for test result `id=2`

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

## Delete a single test result id

HTTP GET
```
{SITE_ROOT}results/delete/5
```

## Delete all the runs except for the most recent 50

HTTP GET
```
{SITE_ROOT}results/delete_oldest_runs_only_keep_newest/50/
```

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
```

Start the development server
```
python start.py
```

Load some test data
```
python load_test_data.py
```

Check that the dashboard seems to be working at http://localhost:8811/results/

Now close the Django development server (new gnome-terminal tab or window created).

Then back in the original terminal shell that has the (dash) Python 3 environment activated:
```
cd /var/www/dash/test-results-dashboard
sudo chmod 666 dash/db.sqlite3
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

```
mkdir c:\git
cd /D c:/git
git clone https://github.com/Qarj/test-results-dashboard
pip install Django
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

Microsoft Visual C++ 14.0 build tools are required, you install them from the Visual Studio 2017 Build Tools
- https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2017 - choose install "Build Tools for Visual Studio 2017"
- Run the installer, click `Visual C++ build tools` (top left option) then the check boxes for `C++/CLI support` and `VC++ 2015.3 v14.00 (v140) toolset for desktop` on the right hand side
- You might need to reboot

Ensure you have Python 3.6.x or higher 32-bit version installed (default from Python.org).
Do not install 64 bit. 

Press Windows Key, type `VS2015` right click `VS2015 x86 Native Tools Command` then select `Run as administrator`
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

then copy the output to httpd.conf after the #LoadModule section

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
cd C:/git/test-results-dashboard/dash/dev
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

