from django.db import models

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

class Produit(models.Model):
    """
        modèle recencant les différents produits proposés à l'abonnement
    """
    #vérifier les choices et paramètres à conserver
    name = models.CharField(
        max_length=3, choices=PRODUITS, default="AFR", unique=True)
