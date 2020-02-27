from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import JSONField

from mflog import get_logger

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
                    'CDPC40_LFPW' : 'VFR',
                    'FPFR42_ATOS' : 'AFR',
                    'FPFR43_FMEE' : 'AOI',
                    'FPFR43_NWBB' : 'ANC',
                    'FPFR43_TFFF' : 'AAG',
}

TIMEZONE = {
                'VFR' : "Europe/Paris",
                'AFR' : "Europe/Paris",
                'AOI' : "Indian/Reunion",
                'ANC' : "Pacific/Noumea",
                'AAG' : "America/Guadeloupe"
            }

logger = get_logger("produit (models)")

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
    
    name = models.CharField(max_length=60)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    reseau = models.DateTimeField()
    reception = models.DateTimeField()
    seuils_grains = JSONField(default=dict())
    seuils_troncons = JSONField(default=dict(), null=True)
    retard = models.BooleanField(default=False)
    statut_carto = models.BooleanField(default=False)
    statut_etats = models.BooleanField(default=False)
    statut_avertissements = models.BooleanField(default=False)
    statut_diffusions = models.BooleanField(default=False)
    statut_acquitements =models.BooleanField(default=False)

    @classmethod
    def create(cls, cdp_file):
        cdp = Cdp()
        cdp.data = cdp_file.read()
        cdp.name = cdp_file.name
        data = [l.decode('utf-8') for l in cdp.data.splitlines()]
        cdp.nom_produit = ENTETES_PRODUITS[cdp.name[:11]]
        header = data[0].split(';')
        cdp.reseau = datetime.strptime(header[0],'%Y%m%d%H%M%S')
        if cdp.nom_produit[0]=='V':
            cdp.seuils_troncons = {l[0]:l[1] for l in data[1:int(header[1])+1]}
            cdp.seuils_grains = {l[0]:l[1] for l in data[int(header[1])+1:]}
        else :
            cdp.seuils_grains = {l[0]:l[3] for l in data[1:]}
        logger.debug(f'{cdp.nom_produit} {cdp.name} {cdp_file.size}')
        return cdp


