from django.db import models
from django.contrib.postgres.fields import JSONField

from helpers.functions import default_emp

PRODUITS = [('AFR','APIC METROPOLE'),
            ('VFR','VF METROPOLE'),
            ('AAG','APIC ANTILLES GUYANE'),
            ('AOI', 'APIC OCEAN INDIEN'),
            ('ANC','APIC NOUVELLE CALEDONIE'),
            ]

ORIGIN_DICO = {
                    'fr':['AFR', 'VFR'],
                    'ga':['AAG'],
                    'ma':['AAG'],
                    're':['AOI'],
                    'nc':['ANC']
                    }

PRODUITS_DICO = {
                    'AFR':['fr'],
                    'VFR':['fr'],
                    'AAG':['ga','ma'],
                    'AOI':['re'],
                    'ANC':['nc']
                    }


class Regle(models.Model):
    """ regle de calcul des avertissements
        fourni un JSON => dict() qui pour chaque clé renvoie True ou False pour diffusion
    """
    name = models.CharField(max_length=25, null=True)
    tableau = JSONField(default=default_emp())
    dt = models.BooleanField()

class Produit(models.Model):
    """
        modèle recencant les différents produits proposés à l'abonnement
    """
    #vérifier les choices et paramètres à conserver
    name = models.CharField(
        max_length=3, choices=PRODUITS, default="AFR", unique=True)
    regle = models.ForeignKey(Regle, on_delete=models.SET_NULL, null=True)


