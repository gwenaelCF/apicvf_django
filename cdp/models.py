from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.files.uploadedfile import InMemoryUploadedFile

#import gzip
import datetime
import csv

from apicvf.models import *

def default_emp():
    return dict()


class BatchCdp(models.Model):
    """ensemble de CdP"""
    name = models.CharField(max_length=80, unique=True)


class Cdp(models.Model):
    class Meta:
        verbose_name = "CdpGlobal"
        verbose_name_plural = "CDPs"
        abstract = True

    # def extract(fichBin):
    #     name = extractName(fichBin)
    #     cdp = gzip.open(fichBin)
    #     header = cdp.readline()

    #     return name, cdp, header

    def __str__(self):
        pass


class CdpApic(Cdp):
    class Meta:
        verbose_name = "Cdp pour les Apic métropole"
        verbose_name_plural = "CDP APIC METROs"
    
    produit = models.CharField(max_length=3, default='AFR')
    name = models.CharField(max_length=80)
    dt = models.DateTimeField()
    grains = JSONField(default=default_emp())
    batch = models.ForeignKey(BatchCdp, to_field="name", on_delete=models.SET_NULL, null=True)

    @classmethod
    def create(cls, fichier_csv_uploaded, batch=None):

        name = 'un_nom'
        #data = fichier_csv.read()
        # reader = csv.reader(fichier_csv)
        # header = reader.__next__()
        # dt_str = header.decode().split(';')[0]
        # dt = datetime.datetime.strptime(dt_str,"%Y%m%d%H%M")
        # grains = {}
        # for row in reader :
        #     grains[row[0]]=row[3]
        return cls(name=name)


# class HistoriCdp(models.Model):
#     produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
#     ts = models.DateTimeField()
#     grain = models.ForeignKey(Grain, to_field="insee", on_delete=models.PROTECT)
#     seuil = models.SmallIntegerField()
    
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields = ['produit', 'ts', 'grain'], name='1grain_1prod_1temps')
#         ]

def extractGrains(cdp, type='apic'):
    grains = {}
    for line in cdp :
        row = line.decode().split(';')
        if len(row[0])==6:
            grains[row[0]]=row[3]
    return grains

def extractName(cdp_bin, type='apic'):
    with open(cdp_bin, 'rb') as f:
        f.read(10)
        a = f.read(1)
        name = ''
        while a!= b'\x00':
            name+=a.decode('latin-1)')
            a=f.read(1)
    return name





