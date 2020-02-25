from django.db import models
from django.contrib.postgres.fields import JSONField

class System(models.Model):
    param = JSONField(default=dict())

class Application(models.Model):
    param = JSONField(default=dict())