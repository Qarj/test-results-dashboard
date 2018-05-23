# test-results-dashboard Task list

## MVP

* Display the dashboard index
* Log Test Name, App Name, Test Result, Random Number, Computer Name, Log Time
    * Create in database
    * Log via API
- Display Test Name, App Name, Test Result, Run Name, Computer Name, Log Time
- Clear out test result data older than 2 days
- Log Test Run Time, Failure Message
- Display Run Time, Failure Message
- Display a single line for all tests with the name random number
- start time, end time, total run time, number of tests, number of failures shown
- Colour of line is red if failure exists, green otherwise
- Can see previous run
- App Owner Tribe and Team
- Running on regression.tjgdev.ds

## Phase II
- Fully aync to log test result - happens on other thread, prove it with delay parameter
- Aync to view results, does not block anything, prove that you can view results and log at same time with delay parameter
- Show results by Tribe
- Drill into previous results

# Web Server Deployment

* Install Apache:
    * From Apache Lounge https://www.apachelounge.com/download/ download Win32 zip file - not 64 bit, then extract so C:\Apache24\bin folder is available.
        * From Admin terminal, `cd C:\Apache\bin` then `httpd -k install` followed by `httpd -k start` (port 80 will need to be free for this to work)

* Install mod_wsgi-express:
    * Follow instructions exactly, and do not mix 32 and 64 bit!
    * Microsoft Visual C++ 14.0 build toosl are required, you install them from the Visual Studio 2017 Build Tools
        * http://landinghub.visualstudio.com/visual-cpp-build-tools - choose install "Visual Studio Build Tools 2017"
        * Run the installer, click `Visual C++ build tools` (top left option) then the checkboxs for `C++/CLI support` and `VC++ 2015.3 v14.00 (v140) toolset for desktop` on the right hand side
        * You might need to reboot
    * Ensure you have Python 3.6.5 32-bit version installed (default from Python.org) Do not install 64 bit. 
    * Press Windows Key, type `VS2015` right click `VS2015 x86 Native Tools Command` then select `Run as administrator`
        * Note: On my Windows 7 machine I had to select `Developer Command Prompt for VS 2017 (2)`
    * Now it will be possible to do `pip install mod_wsgi`

* Verify wsgi install with a Hello World app:
    * `copy C:\git\test-results-dashboard\tests\hello_world\httpd-vhosts_windows.conf C:\Apache24\conf\extra\httpd-vhosts.conf`
    * `notepad C:\Apache24\conf\httpd.conf` then uncomment `Include conf/extra/httpd-vhosts.conf`
    * `mod_wsgi-express module-config` then copy the output to httpd.conf after the #LoadModule section
    * `httpd -k restart`
    * verify with url: http://localhost/hello_world

* Note - the output from `mod_wsgi-express module-config` will look a bit like:
```
LoadFile "c:/python36/python36.dll"
LoadModule wsgi_module "c:/python36/lib/site-packages/mod_wsgi/server/mod_wsgi.cp36-win32.pyd"
WSGIPythonHome "c:/python36"
```

* Configure Django to use Apache:
    * `copy C:\git\test-results-dashboard\dash\httpd-vhosts_windows.conf C:\Apache24\conf\extra\httpd-vhosts.conf`
    * `httpd -k restart`
    * verify with url: http://localhost/dash/results

# Linux Deployment

sudo apt update
sudo apt install apache2

If a firewall exists:
sudo ufw allow 'Apache'
sudo ufw status

Confirm Apache is running:
sudo systemctl status apache2

Common commands:
sudo systemctl stop apache2
sudo systemctl start apache2
sudo systemctl restart apache2
sudo systemctl reload apache2
sudo systemctl disable apache2
sudo systemctl enable apache2
cat /etc/apache2/envvars
cat /var/log/apache2/error.log

Install mod wsgi:
sudo apt install apache2-dev
pip3 install mod_wsgi
mod_wsgi-express module-config | sudo tee /etc/apache2/conf-enabled/wsgi.conf
sudo cp ~/git/test-results-dashboard/dash/httpd-vhosts_linux.conf /etc/apache2/sites-enabled/test-results-dashboard.conf
sudo systemctl restart apache2
verify with url: http://localhost/dash/results


https://github.com/GrahamDumpleton/mod_wsgi/issues/308
Create a directory something like /var/www/project. Change the ownership to you. Put in that directory the virtual environment and your project code with everything owned by you. Directories and files need to be accessible to other users so that the Apache user can access it. Install packages into the virtual environment as you. Set up mod_wsgi to use your project from that location.


## References
* https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/modwsgi/
* https://stackoverflow.com/questions/42298503/how-to-install-mod-wsgi-for-apache-2-4-and-python-3-4-on-windows?noredirect=1&lq=1
* https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html
* https://modwsgi.readthedocs.io/en/develop/getting-started.html
* https://pypi.org/project/mod_wsgi/
* https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7
* https://groups.google.com/forum/#!forum/modwsgi


