# test-results-dashboard Task list

## Phase II
- Clean up artefacts
- Fully aync to log test result - happens on other thread, prove it with delay parameter
- Aync to view results, does not block anything, prove that you can view results and log at same time with delay parameter
- Show results by Tribe
- Drill into previous results
- Tidy up root folder
    - Linux and Windows should be common
    - Move to setup / quickstart folder

# Linux Deployment Notes

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


## References
* https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/modwsgi/
* https://stackoverflow.com/questions/42298503/how-to-install-mod-wsgi-for-apache-2-4-and-python-3-4-on-windows?noredirect=1&lq=1
* https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html
* https://modwsgi.readthedocs.io/en/develop/getting-started.html
* https://pypi.org/project/mod_wsgi/
* https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-centos-7
* https://groups.google.com/forum/#!forum/modwsgi
* http://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html

