from django.db import models

# Create your models here.

class Result(models.Model):
    test_name = models.CharField(max_length=200)
    app_name = models.CharField(max_length=50)
    test_passed = models.NullBooleanField(default=None)
    run_name = models.CharField(max_length=20)
    run_server = models.CharField(max_length=30)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    message = models.CharField(max_length=200, null=True, blank=True)
