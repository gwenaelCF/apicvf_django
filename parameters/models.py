from django.db import models
from django.contrib.postgres.fields import JSONField

class System(models.Model):
    key = models.CharField(max_length=100, unique = True)
    value = models.CharField(max_length=100)

class Application(models.Model):
    key = models.CharField(max_length=100, unique = True)
    value = models.CharField(max_length=100)