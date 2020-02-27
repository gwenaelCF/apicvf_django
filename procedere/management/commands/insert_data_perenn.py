import csv
import time
import os

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.apps import apps

from procedere import models

class Command(BaseCommand):
    help='''
    commande pour injecter les données fixes sur une base
    | force une ou plusieurs options parmi :
      * regles - produits - grains - etats - tout *
      (nb : tout supplante tout autre)
    '''
    requires_migrates_checks = True



    def add_arguments(self, parser):
        parser.add_argument('todo', nargs='+', type=str)
        parser.add_argument('-d', type=str, default="", help="Répertoire dans lequel trouver les fichiers d'entrée relativement au manage.py.")


    def handle(self, *args, **options):
        def insert_regles(data):
            qs = models.produit.Regle.objects.all().values_list('name', flat=True)
            for regle in serializers.deserialize('json',data):
                if regle.object.name not in qs :
                    regle.save()

        def insert_produits():

            for entete, prod in models.produit.ENTETES_PRODUITS.items():
                new_prod = models.produit.Produit(shortname=prod, entete=entete, name=prod)
                reg = 'apic' if new_prod.name[0]=='A' else 'vf'
                new_prod.regle = models.produit.Regle.objects.get(name=reg)
                try :
                    new_prod.save()
                except :
                    pass

        def insert_region(dicteur):
            liste_reg = []
            for d in dicteur:
                reg = models.granularite.Region(insee=d['reg'])
                for l in ['cheflieu', 'tncc', 'ncc', 'nccenr', 'libelle']:
                    setattr(reg,l,d[l])
                if int(reg.insee)<=9:
                    reg.metrop=False
                liste_reg.append(reg)
            models.granularite.Region.objects.bulk_create(liste_reg, batch_size=1000)

        def insert_dept(dicteur):
            liste_dept = []
            liste_reg = models.granularite.Region.objects.only('id', 'insee', 'metrop')
            for d in dicteur:
                dept = models.granularite.Dept(insee=d['dep'])
                for l in ['cheflieu', 'tncc', 'ncc', 'nccenr', 'libelle']:
                    setattr(dept,l,d[l])
                dept.region=liste_reg.get(insee=d['reg'])
                dept.metrop = dept.region.metrop
                liste_dept.append(dept)
            models.granularite.Dept.objects.bulk_create(liste_dept, batch_size=1000)

        def insert_grain(dicteur):
            liste_grain = []
            liste_dept = models.granularite.Dept.objects.only('id', 'insee', 'metrop')
            for d in dicteur:
                if d['typecom'] in ['COM', 'ARM']:
                    grain = models.granularite.Grain(insee=d['com'])
                    for l in ['dep', 'arr', 'tncc', 'ncc', 'nccenr', 'libelle']:
                        if d[l]:
                            setattr(grain,l,d[l])
                    if d['dep']:
                        grain.dept =  liste_dept.get(insee=d['dep'])
                        grain.metrop = grain.dept.metrop
                    liste_grain.append(grain)
            models.granularite.Grain.objects.bulk_create(liste_grain, batch_size=5000)


        def insert_etat(dicteur):
            dico_etat = {'reg':[],'dep':[],'grain':[]}
            oridict = {}
            for d in dicteur:
                oridict.setdefault(d['origin'], []).append(d['id'])
            for produit in models.produit.Produit.objects.all():
                models.etat.EtatProduit.objects.get_or_create(produit=produit)
                insee_produit = [
                    insee for orig in models.produit.PRODUITS_ORIGIN[produit.shortname] 
                            for insee in oridict[orig]
                            ]
                grains_temp, dept_temp = [], []
                gr_qs = models.granularite.Grain.objects.filter(
                                            insee__in=insee_produit)
                for grain in gr_qs:
                    g = models.etat.EtatGrainProduit(
                                        produit=produit, grain = grain)
                    grains_temp.append(g)
                dep_qs = models.granularite.Dept.objects.filter(
                                        id__in=set(gr_qs.values_list('dept',flat=True))
                                        )
                for dept in dep_qs:
                    d = models.etat.EtatDeptProduit(produit=produit, dept = dept)
                    dept_temp.append(d)
                for reg in models.granularite.Region.objects.filter(
                                        id__in=set(dep_qs.values_list('region', flat=True))): 
                    r = models.etat.EtatRegionProduit(produit=produit, reg = reg)
                    dico_etat['reg'].append(r)
                dico_etat['grain'].extend(grains_temp)
                dico_etat['dep'].extend(dept_temp)

            models.etat.EtatRegionProduit.objects.bulk_create(
                                dico_etat['reg'], batch_size=1000)
            models.etat.EtatDeptProduit.objects.bulk_create(
                                dico_etat['dep'], batch_size=1000)
            models.etat.EtatGrainProduit.objects.bulk_create(
                                dico_etat['grain'], batch_size=5000)
        

        allowed = ['regles','produits', 'grains' ,'etats', 'tout']

        todo = options['todo']
        for td in options['todo']:
            if td not in allowed :
                raise CommandError('option "{}" not allowed (should be in {})'.format(td,allowed))
        regles = 'regles' in todo
        produits = 'produits' in todo
        grains = 'grains' in todo
        etats = 'etats' in todo
        tout = 'tout' in todo


        path_procedere = apps.get_app_config('procedere').path
        filepath = os.path.join(path_procedere, 'data')
        if options['d']:
            filepath = os.path.join(path_procedere, options['d'])
        fileregle = os.path.join(filepath,'regles.json')
        filereg = os.path.join(filepath,'region2019.csv')
        filedept = os.path.join(filepath,'departement2019.csv')
        filecom = os.path.join(filepath,'communes_all.csv')
        fileorigin = os.path.join(filepath,'communes_origin.csv')

        t_start = time.time()
        if tout or regles:
            self.stdout.write(self.style.NOTICE('insertion regles'))
            data = open(fileregle,'r')
            insert_regles(data)

        if tout or produits:
            self.stdout.write(self.style.NOTICE('insertion produits'))
            insert_produits()
            t_int1 = time.time()
            self.stdout.write(self.style.NOTICE(
                f'regles et produits faits en {t_int1-t_start}'))
        else:
            t_int1 = time.time()

        #list_com, list_dept, list_reg = [], [], []
        if tout or grains:
            self.stdout.write(self.style.NOTICE('création regions'))
            with open(filereg,'r',encoding='utf-8-sig') as f:
                dicteur = csv.DictReader(f) 
                insert_region(dicteur)
            t_int2 = time.time()
            self.stdout.write(self.style.NOTICE(f'done in {t_int2-t_int1}'))    
            self.stdout.write(self.style.NOTICE('création dept'))
            with open(filedept,'r',encoding='utf-8-sig') as f:
                dicteur = csv.DictReader(f) 
                insert_dept(dicteur)
            t_int3 = time.time()
            self.stdout.write(self.style.NOTICE(f'done in {t_int3-t_int2}'))
            self.stdout.write(self.style.NOTICE('création grains'))
            with open(filecom,'r',encoding='utf-8-sig') as f:
                dicteur = csv.DictReader(f) 
                insert_grain(dicteur)
            t_int4 = time.time()
            self.stdout.write(self.style.NOTICE(f'done in {t_int4-t_int3}'))
        else:
            t_int4 = time.time()

        if tout or etats:
            self.stdout.write(self.style.NOTICE('création etats par produit'))
            with open(fileorigin,'r', encoding='utf-8-sig') as f:
                dicteur = csv.DictReader(f, delimiter=';')
                insert_etat(dicteur)
            t_int5 = time.time()
            self.stdout.write(self.style.NOTICE(f'done in {t_int5-t_int4}'))

        t_fin = time.time()
        self.stdout.write(self.style.NOTICE(f'total secondes {t_fin-t_start}'))
            

        



