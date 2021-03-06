from django.db import models

from django.db.models.signals import post_delete
from django.dispatch import receiver

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
    team_name = models.CharField(max_length=20, default=None, blank=True, null=True)

class Artefact(models.Model):
    test_name = models.CharField(max_length=200)
    app_name = models.CharField(max_length=50)
    run_name = models.CharField(max_length=20)
    name = models.CharField(max_length=160)
    desc = models.CharField(max_length=200)
    document = models.FileField(upload_to='artefacts/%Y/%m/%d/', default=None)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

@receiver(post_delete, sender=Artefact)
def submission_delete(sender, instance, **kwargs):
    instance.document.delete(False)