# test-results-dashboard Task list

# Current
x remove test_name, run_name and app_name from Artefact save so we don't need to worry about file name safe issues & file deletion
x only load documents on final state in load_test_data.py, not pend
x load dom example
x does test file work under Apache - Windows
x review load scripts for linux and windows
x does test file work under Apache - Linux
x update README for read_file
x logging same asset name twice should overwrite, or not cause errors
x put assets in table
x show asset description
x draw border around table
x show asset offset time (i.e. from Start Time delta)
- understand deletion bugs
    - the bug is that it is not deleting the oldest, perhaps the oldest per day
- include artefacts in deletion
- add method to delete test older than days


## Phase II
- Fully async to log test result - happens on other thread, prove it with delay parameter
- Async to view results, does not block anything, prove that you can view results and log at same time with delay parameter
- Show results by Tribe
- Drill into previous results

# Linux Deployment Notes

If a firewall exists:
```
sudo ufw allow 'Apache'
sudo ufw status
```

Confirm Apache is running:
```
sudo systemctl status apache2
```

Common commands:
```
sudo systemctl stop apache2
sudo systemctl start apache2
sudo systemctl restart apache2
sudo systemctl reload apache2
sudo systemctl disable apache2
sudo systemctl enable apache2
cat /etc/apache2/envvars
cat /var/log/apache2/error.log
```

## References
* https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/modwsgi/
* https://stackoverflow.com/questions/42298503/how-to-install-mod-wsgi-for-apache-2-4-and-python-3-4-on-windows?noredirect=1&lq=1
* https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html
* https://modwsgi.readthedocs.io/en/develop/getting-started.html
* https://pypi.org/project/mod_wsgi/
* https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7
* https://groups.google.com/forum/#!forum/modwsgi
* http://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html

