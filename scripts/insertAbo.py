import random
from itertools import islice, chain, repeat

from injectionCdP import models
from django.db.models import F
from django.db.models.functions import Concat
from django.db.models import TextField, Value as V

aboNat = 15
aboDep = 1 #ATTENTION, coef multiplicateur par nombre total de départements
aboCom = 10000

empNat = {'nat':True}

def empCom():
    '''création d'une emprise aléatoire sur des communes d'un mm département'''
    # r = id dept en base, peu robuste
    r = random.randint(1,97)
    nbCom = random.randint(4,10)
    com = []
    for c in models.Grain.objects.filter(dept_id=r)[:nbCom]:
        com.append(c.id)
    return com

def empDep():
    return models.Dept.objects.all()


def bulkCreateAbo(newAbos):
    batchSize= 1000
    while True:
        batch = list(islice(newAbos, batchSize))
        if not batch:
            break
        models.Abonnement.objects.bulk_create(batch, batchSize)

def createAbo():
    print(f'création de {aboNat} abo nationaux, de {aboDep} * 101 abo départementaux et de {aboCom} abo zones de communes')
    
    
    prod, created = models.Produit.objects.get_or_create(name='A')
    #aboNat
    bulkCreateAbo((models.Abonnement(emprise_nat=True, produit = prod) for _ in range(aboNat)))
    #add abo to the etatdept aboList (splitted from the previous op to be removed if not needed)
    for abo in models.Abonnement.objects.filter(emprise_nat=True):
        # put the update in a function when tests are done
        models.EtatDeptProduit.objects.all().update(aboList=Concat(F('aboList'),V(str(abo.id)+';'), output_field=TextField()))
    
    #aboDep
    # can be generate in onliner, let it be more clear
    aboDeptList = []
    for abo, dep in ((models.Abonnement(emprise_nat=False, produit = prod), dep) for dep in chain(*repeat(empDep(),aboDep))):
        abo.save()
        abo.emprise_dept.set([dep])
        models.EtatDeptProduit.objects.filter(dept__exact=dep).update(aboList=Concat(F('aboList'),V(str(abo.id)+';'), output_field=TextField()))

    
    #aboCom
    for abo in (models.Abonnement(emprise_nat=False, produit = prod) for _ in range(aboCom)):
        gList = empCom()
        abo.save()
        abo.emprise_grain.set(gList)
        #following is not working, can't say why
        models.EtatGrainProduit.objects.filter(grain__id__in=gList).update(aboList=Concat(F('aboList'),V(str(abo.id)+';'), output_field=TextField()))

#mettre dans un autre script
def createAllEtat():
    #countEtatGrain, countEtatDept = 0, 0
    for prod in models.Produit.objects.all():
        for grain in models.Grain.objects.all():
            models.EtatGrainProduit.objects.get_or_create(produit=prod, grain = grain)
        for dept in models.Dept.objects.all():
            models.EtatDeptProduit.objects.get_or_create(produit=prod, dept = dept)


def run(*args):
    createAllEtat()
    createAbo()


