from django.db import models
from django.contrib.postgres.fields import JSONField


PRODUITS = [('AFR','APIC METROPOLE'),
            ('VFR','VF METROPOLE'),
            ('AAG','APIC ANTILLES GUYANE'),
            ('AOI', 'APIC OCEAN INDIEN'),
            ('ANC','APIC NOUVELLE CALEDONIE'),
            ]

COUVERTURE_PRODUITS = {
                    'fr':['AFR', 'VFR'],
                    'ga':['AAG'],
                    'ma':['AAG'],
                    're':['AOI'],
                    'nc':['ANC']
                    }

PRODUITS_ORIGIN = {
                    'AFR':['fr'],
                    'VFR':['fr'],
                    'AAG':['ga','ma'],
                    'AOI':['re'],
                    'ANC':['nc']
                    }

ENTETES_PRODUITS = {
                    'CDPC40LFPW' : 'VFR',
                    'FPFR42ATOS' : 'AFR',
                    'FPFR43FMEE' : 'AOI',
                    'FPFR43NWBB' : 'ANC',
                    'FPFR43TFFF' : 'AAG',
}


class Regle(models.Model):
    """ regle de calcul des avertissements
        fourni un JSON => dict() qui pour chaque clé renvoie True ou False pour diffusion
    """
    name = models.CharField(max_length=40, null=True)
    tableau = JSONField(default=dict())
    ## !!! vérifier options !!!
    dt = models.DurationField(null=True)

class Produit(models.Model):
    """
        modèle recensant les différents produits proposés à l'abonnement
    """
    #vérifier les choices et paramètres à conserver
    shortname = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=40)
    regle = models.ForeignKey(Regle, on_delete=models.PROTECT)
    entete = models.CharField(max_length=12, unique=True)
    grains = JSONField(default=dict())
    couverture = models.CharField(max_length=12)
    timezone = models.CharField(max_length=40)
    

class Cdp(models.Model):
    """ classe liant un fichier de grain:seuil pour un réseau à un produit """
    
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    reseau = models.DateTimeField()
    reception = models.DateTimeField()
    seuils_grains = JSONField(default=dict())
    retard = models.BooleanField(default=False)
    etats_grains_produit = models.BooleanField(default=False)
    avertissements = models.BooleanField(default=False)
    diffusions = models.BooleanField(default=False)
    acquitements =models.BooleanField(default=False)

    @classmethod
    def create(cls, cdp_file):
        cdp = Cdp()
        name = cdp_file.name

