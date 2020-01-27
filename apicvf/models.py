from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

def default_etat():
    # les réseaux sont instanciés à 0 pour t-2...t
    return {'t-2':0,'t-1':0,'t0':0}

def default_emp():
    # les emprises sont vides (sûrement instanciées plus tard en fonction du compte)
    return dict()

#mettre en place des clés lorsque la liste sera établie
# a mettre dans les config admin
PRODUITS = [('AFR','APIC METROPOLE'),
            ('VFR','VF METROPOLE'),
            ('AAG','APIC ANTILLES GUYANE'),
            ('AOI', 'APIC OCEAN INDIEN'),
            ('ANC','APIC NOUVELLE CALEDONIE'),
            ]


class Produit(models.Model):
    name = models.CharField(max_length=10, choices=PRODUITS, default="AFR")

class Granularite(models.Model):
    """ classe mère reprenant les info INSEE """
    insee = models.CharField(max_length=2, unique=True)
    tncc = models.SmallIntegerField(null=True)
    ncc = models.CharField(max_length=200, null=True)
    nccenr = models.CharField(max_length=200, null=True)
    libelle = models.CharField(max_length=200, null=True)
    metrop = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Region(Granularite):
    """ ensemble de departements """
    cheflieu = models.CharField(max_length=200, null=True)
    
class Dept(Granularite):
    """ ensemble de grains """
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    cheflieu = models.CharField(max_length=200, null=True)

class Grain(Granularite):
    """ plus petit référentiel géopgraphique ayant un seuil d'avertissement """
    dept = models.ForeignKey(Dept, on_delete=models.PROTECT, null=True)
    arr = models.CharField(max_length=4, null=True)
    cp = models.CharField(max_length=6, null=True)
    
class Etat(models.Model):
    """ classe mère liant les produits et les granularités par applât"""
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    t_2= models.SmallIntegerField(default=0)
    t_1= models.SmallIntegerField(default=0)
    t0 = models.SmallIntegerField(default=0)
    abo_array = ArrayField(models.IntegerField(blank=True),blank=True, null=True) 

    class Meta :
        abstract = True

class Etat_reg_produit(Etat):
    # vérifier le besoin d'un applatissement par région
    # non-implentée pour le moment
    reg = models.ForeignKey(Region, on_delete=models.PROTECT)

    class Meta :
        abstract = True

class Etat_dept_produit(Etat):
    dept = models.ForeignKey(Dept, on_delete=models.PROTECT)
    
class Etat_grain_produit(Etat):
    grain = models.ForeignKey(Grain, on_delete=models.PROTECT)

class Souscription(Etat):
    """ abonnement 'conglomérat' sur les sous-ensembles d'un produit """
    derniere_alerte = models.DateTimeField(null=True)
    derniere_alerte_ensemble = ArrayField(models.IntegerField(blank=True),blank=True, null=True)
    derniere_alerte_seuil = models.SmallIntegerField(default=0)

    @classmethod
    def is_alert():
        """ FOR ETAT_DEPT_PRODUIT WHERE PRODUIT==PRODUIT:
        IF ETAT_DEPT_PRODUIT.alert==ALERT:
            souscription.alert = MAX(souscription.alert, ETAT_DEPT_PRODUIT) """
        pass

class Abonnement(models.Model):
    """ abonnements """
    # à voir si l'on a besoin de rappeler le produit ici (redondance mais peut accélérer le rappel)
    #produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    
    #gérér les comptes ici
    ## créer des comptes, ce serait utile
    
    #gérér les emprises ci-dessous
    emprise_reg_array = ArrayField(models.IntegerField(blank=True),blank=True, null=True)
    emprise_dept_array = ArrayField(models.IntegerField(blank=True),blank=True, null=True)
    emprise_grain_array = ArrayField(models.IntegerField(blank=True),blank=True, null=True)
    
    #gérer les alertes là
    derniere_alerte = models.DateTimeField(null=True)
    derniere_alerte_ensemble = ArrayField(models.IntegerField(blank=True),blank=True, null=True)
    derniere_alerte_seuil = models.SmallIntegerField(default=0)
    
    #type de compte (applat/conglo), si True, pas d'emprise
    souscription = models.BooleanField(default=False)

  
# class Avertissement(models.Model):
#     #créer un models.ARCHIVE pour archiver les abo effacés
#     abo = models.ForeignKey(Abonnement, on_delete=models.PROTECT)
#     dts = models.DateTimeField()
#     seuil = models.SmallIntegerField()
#     emprise_alerte = JSONField(null=True)
