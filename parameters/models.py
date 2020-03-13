"""
Param
"""
from django.db import models

class Param(models.Model):
    """
    classe mère pour les paramètres
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100)

    class Meta:
        abstract = True

    @classmethod
    def get_value(cls, key):
        """
        retourne le paramètre demandé
        """
        return cls.objects.get(key=key).value

    @classmethod
    def set_value(cls, key, value):
        """
        ajoute (ou MAJ) le paramètre
        """
        cls.objects.update_or_create(
            key=key, defaults={'value': value}
        )

class System(Param):
    """
    paramètres de type system
    """

class Application(Param):
    """
    paramètres de type application
    """
