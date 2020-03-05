from django.db import models


class Granularite(models.Model):
    """ classe mère reprenant les info INSEE """
    insee = models.CharField(max_length=6, unique=True)
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
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    cheflieu = models.CharField(max_length=200, null=True)


class Grain(Granularite):
    """ plus petit référentiel géopgraphique ayant un seuil d'avertissement """
    dept = models.ForeignKey(Dept, on_delete=models.PROTECT, null=True)
    arr = models.CharField(max_length=4, null=True)
    cp = models.CharField(max_length=6, null=True)
