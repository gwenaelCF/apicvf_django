from django.db import models
from django.contrib.postgres.fields import ArrayField
from .produit import Produit
from .granularite import *


class Etat(models.Model):
    """ classe mère liant les produits et les granularités
    seuil maximal conservé pour les 3 derniers réseaux
    les abonnements sont listés pour chaque emprise concernée
    """

    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    t_2 = models.SmallIntegerField(default=0)
    t_1 = models.SmallIntegerField(default=0)
    t0 = models.SmallIntegerField(default=0)
    reseau = models.DateTimeField(null=True)
    abo_array = ArrayField(models.IntegerField(
        blank=True), blank=True, null=True)

    class Meta:
        abstract = True


class EtatRegionProduit(Etat):
    """ état des régions par produit """
    reg = models.ForeignKey(Region, on_delete=models.PROTECT)


class EtatDeptProduit(Etat):
    """ état des départements par produit """
    dept = models.ForeignKey(Dept, on_delete=models.PROTECT)


class EtatGrainProduit(Etat):
    """ état des grains par produit """
    grain = models.ForeignKey(Grain, on_delete=models.PROTECT)


class EtatProduit(Etat):
    """ état de l'ensemble des grains d'un produit """
    pass
