from django.db import models
from django.contrib.postgres.fields import JSONField

class System(models.Model):
    key = models.CharField(max_length=100, unique = True)
    value = models.CharField(max_length=100)

class Application(models.Model):
    key = models.CharField(max_length=100, unique = True)
    value = models.CharField(max_length=100)

def get_value(classe, key):
    """ 
    retourne le paramètre demandé 
    """
    if classe not in ['app', 'sys']:
        raise ValueError('classe doit être `app` ou `sys`')
    classe = Application if classe=='app' else System
    
    return classe.objects.get(key=key).value

def set_value(classe, key, value):
    """ 
    ajoute (ou MAJ) le paramètre
    """
    if classe not in ['app', 'sys']:
        raise ValueError('classe doit être `app` ou `sys`')
    classe = Application if classe=='app' else System
    
    # set value (or update if exist)
    classe.objects.update_or_create(
        key=key, defaults={'value': value}
    )
