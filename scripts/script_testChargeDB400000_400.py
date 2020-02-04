import time
import random

from django.db.models import Max, Min, F

import injectionCdP


#
#helpers
class Timer(object):  
    def __enter__(self):  
        self.start()  
        # __enter__ must return an instance bound with the "as" keyword  
        return self  
      
    # There are other arguments to __exit__ but we don't care here  
    def __exit__(self, *args, **kwargs):   
        self.stop()  
      
    def start(self):  
        if hasattr(self, 'interval'):  
            del self.interval  
        self.start_time = time.time()  
  
    def stop(self):  
        if hasattr(self, 'start_time'):  
            self.interval = time.time() - self.start_time  
            del self.start_time

def whatTimeIsIt():
    return time.strftime("%d %b %Y %H:%M:%S", time.localtime())

#
#fonctions de comparaison
def seuilCompar(x):
    # 0<-1<1<2
    return (2*(x**2)+x)

def findMax(l):
    return max(set(l), key=seuilCompar)

#
#règle métier
def reglApic(obj):
    t0 = obj.t0
    t_1 = obj.t_1
    t_2 = obj.t_2
    if t0:
        if (t0==-1 and t_1==-1 and t_2!=-1):
            return True
        if (t_1==0 or t0>max(t_2,t_1)):
            return True
    return False

#
#update en base
def modifSeuilBatch(obj, t0):
    obj.update(t_2=F('t_1'))
    obj.update(t_1=F('t0'))
    obj.update(t0=int(t0))

def modifSeuilUnit(obj, newT0):
    """modif l'objet pas la base si .save() est commenté"""
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    #obj.save()
    return obj

#
#fonctions d'injection de cdp simplifiées pour grains
def randomChoice(nbGrains, weights=[9985, 9990, 9999, 10000]):
    return random.choices([0,-1,1,2], cum_weights= weights, k=nbGrains)

def injectCdPRandom(nbGrains, minId, weights):
    fakeCdp = randomChoice(nbGrains, weights)
    seuils = {0:[],-1:[],1:[],2:[]}
    print(f'seuils généré, création dico des seuils de grains')
    with Timer() as t:
        for i in range(len(fakeCdp)):
            seuils[fakeCdp[i]].append(i+minId)
        # for key in seuils.keys():
        #     modifSeuilBatch(
        #         injectionCdP.models.EtatGrainProduit.objects.filter(
        #             grain_id__in=seuils[key]),
        #             key
        #             )
    print(f'fait en {t.interval}')
    return seuils

#
#les abonnements
def updateAbo(seuils):
    with Timer() as t:
        dicoAbo = {0:[],-1:[],1:[],2:[]}
        alertAbo = {-1:0,1:0,2:0}
        etat_qs = injectionCdP.models.EtatGrainProduit.objects.values(
            'id','grain__insee','t_2', 't_1', 't0','aboArray')
        for key in dicoAbo.keys():
            for idEtat in seuils[key]:
                dicoAbo.append(etat_qs.get(id=idEtat))
        
        for abo in injectionCdP.models.Abonnement.objects.prefetch_related('emprise_grain'):
            newT0 = findMax(abo.emprise_grain.values_list('t0', flat=True))
            abo = modifSeuilUnit(abo, newT0)
            dicoAbo[newT0].append(abo)
            if reglApic(abo):
                alertAbo[newT0]+=1
        for key in dicoAbo.keys():
            modifSeuilBatch(dicoAbo[key],key)
    print(f'abonnements mis à jour en {t.interval}')
    return alertAbo

#
#fonctions de mise en place de db (!!! db existante avec grains et etatgrains mais sans abo !!!)
def randomAboSurGrains(minId, maxId, nb):
    return injectionCdP.models.EtatGrainProduit.objects.filter(
        grain_id__in=random.sample(range(minId,maxId),nb))

def createAbo(nbAbo, grainParAbo, grains, minId, maxId):
    # print(f'création de {nbAbo} abo')
    # with Timer() as t:
    #     injectionCdP.models.Abonnement.objects.bulk_create(
    #         (injectionCdP.models.Abonnement(produit_id=1) for _ in range(nbAbo))
    #         )
    # print(f'fait en {t.interval}')
    print(f'rattachement à {grainParAbo} grains')
    with Timer() as t:
        ql = injectionCdP.models.Abonnement.objects.filter(emprise_grain__isnull=True)
        for abo in ql:
            abo.emprise_grain.set(randomAboSurGrains(minId, maxId, grainParAbo))
    print(f'fait en {t.interval}')


def run(weights=[9985, 9990, 9999, 10000], cycles=1):
    print(f'starting at : {whatTimeIsIt()}')
    
    #param, oui perdus ici
    nbAbo= 400000
    grainParAbo = 400

    print(f'param : abo={nbAbo}, grainParAbo={grainParAbo}, proba_cumulative[0,-1,1,2]={weights}, cycles={cycles}')
    #useful var
    grain_range = injectionCdP.models.Grain.objects.aggregate(Max('id'),Min('id'))
    grainsQl = injectionCdP.models.Grain.objects.all()
    nbGrains = grainsQl.count()
    #coffee break
    #createAbo(nbAbo, grainParAbo, grainsQl, grain_range['id__min'], grain_range['id__max'])
    time = 0
    for j in range(cycles):
        print(f"cycle {j+1} - injection d'un cdp")
        seuils = injectCdPRandom(nbGrains, grain_range['id__min'], weights)
        print(f"mise à jour des abonnements")
        alertAbo = updateAbo(seuils)
        print(f'nombre d\'abo en alerte par seuil : \n{alertAbo}')

    print(f'end at : {whatTimeIsIt()}')



##### temp save
abo_sur_seuil = injectionCdP.models.EtatGrainProduit.objects.filter(
    id=seuil['id']
    ).values_list(
    'abonnement__id',flat=True
    )

