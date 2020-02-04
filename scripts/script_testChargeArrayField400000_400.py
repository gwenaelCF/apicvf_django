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


#inversion dict
def invert_dict(dico):
    for key, value in dico.items():
        for i in value:
            dicinv.setdefault(i, []).append(key)
    return dicinv


#
#règle métier

#fonctions de comparaison
def seuilCompar(x):
    # 0<-1<1<2
    return (2*(x**2)+x)

def findMax(l):
    return max(set(l), key=seuilCompar)

def regl_apic_obj(obj):
    t0 = obj.t0
    t_1 = obj.t_1
    t_2 = obj.t_2
    if t0:
        if (t0==-1 and t_1==-1 and t_2!=-1):
            return True
        if (t0!=-1 and t_1==0) or t0>max(t_2,t_1):
            return True
    return False

def regl_apic_seuils(t_2,t_1,t0):
    if t0:
        if (t0==-1 and t_1==-1 and t_2!=-1):
            return True
        if (t0!=-1 and t_1==0) or t0>max(t_2,t_1):
            return True
    return False
#
#update en base
def modifSeuilBatch(obj, t0):
    #en base
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
def randomChoice(insee_list, weights=[9985, 9990, 9999, 10000]):
    return random.choices([0,-1,1,2], cum_weights= weights, k=insee_list)

def injectCdPRandom(insee_list, weights):
    print(f'génération cdp')
    with Timer() as t:
        randList = randomChoice(len(insee_list), weights)
        fakeCdp = {insee_list[i]:randList[i] for i in range(len(insee_list))}    
    print(f'fait en {t.interval}')
    return fakeCdp

def updateGrainDB(fakeCdp):
    seuils = {0:[],-1:[],1:[],2:[]}
    with Timer() as t:
        print(f'création dico des seuils de grains')    
        for insee, seuil in fakeCdp.items():
            seuils[seuil].append(insee)
        print(f'update (état)grains en base')
        for key in seuils.keys():
            modifSeuilBatch(
                    injectionCdP.models.EtatGrainProduit.objects.filter(
                        grain__insee__in=seuils[key]),
                    key
            )
    print(f'fait en {t.interval}')

#
#les abonnements
def updateAboDB(dico_abo_etat0):
    with Timer() as t:
        seuils = {-1:[],1:[],2:[]}
        for abo, value in dico_abo_etat0.items():
            seuils[value[2]].append(abo)
        abo2change = []
        for key, abolist in seuils.items():
            abo2change = abo2change + abolist
            modifSeuilBatch(injectionCdP.models.Abonnement.objects.filter(id__in=abolist),key)
        modifSeuilBatch(injectionCdP.models.Abonnement.objects.exclude(id__in=abo2change), 0)
    print(f'abonnements mis à jour en {t.interval}')


def applatissement(fakeCdp):
    print(f'début applatissement')

    #rajouter le produit en condition réelle !!!
    #filtrer avec le CDP !!!!
    etat_qs = injectionCdP.models.EtatGrainProduit.objects.values(
        'id','grain__insee','t_2', 't_1', 't0','aboArray')
    alertAbo = {-1:0,1:0,2:0}
    with Timer() as t:
        dico_etat_abo = {etat['grain__insee']:(etat['aboArray'],etat['t_2'], etat['t_1'], etat['t0']) 
                            for etat in etat_qs
                        }
    print(f'dico des etats grains fait en {t.interval}')        
    with Timer() as t:
        #dico_abo_etat = invert_dict(dico_etat_abo)
        dico_abo_etat0 = {}
        for insee, newt0 in fakeCdp.items():
            if newt0 != 0:
                for abo in dico_etat_abo[insee][0]:
                    dico_abo_etat0.setdefault(abo, []).append(
                        (dico_etat_abo[insee][2], dico_etat_abo[insee][3], newt0)
                        )
        for abo, etats in dico_abo_etat0.items():
            etats = [findMax(seuils) for seuils in zip(*etats)]
            #print(etats)
            dico_abo_etat0[abo]=etats
            if regl_apic_seuils(etats[0],etats[1],etats[2]):
                alertAbo[etats[2]]+=1
        #print(dico_abo_etat0)
    print(f'applatissement fait en {t.interval}')
    return dico_etat_abo, dico_abo_etat0, alertAbo




def run(weights=[0, 10000, 10000, 10000], cycles=3):
    print(f'starting at : {whatTimeIsIt()}')
    
    #param, oui perdus ici
    nbAbo= 400000
    grainParAbo = 400

    print(f'param : abo={nbAbo}, grainParAbo={grainParAbo}, proba_cumulative[0,-1,1,2]={weights}, cycles={cycles}')
    #useful var
    # grain_range = injectionCdP.models.Grain.objects.aggregate(Max('id'),Min('id'))
    # grainsQl = injectionCdP.models.Grain.objects.all()
    # nbGrains = grainsQl.count()
    insee_list = list(injectionCdP.models.Grain.objects.values_list('insee', flat=True))
    time = 0
    for j in range(cycles):
        with Timer() as t:
            print(f"cycle {j+1} - injection d'un cdp")
            fakeCdp = injectCdPRandom(insee_list, weights)
            print(f'traitement')
            dico_etat_abo, dico_abo_etat0, alertAbo = applatissement(fakeCdp)
            print(f'nombre d\'abo en alerte par seuil : \n{alertAbo}')
            print(f"mise à jour base")
            updateGrainDB(fakeCdp)
            #updateAboDB(dico_abo_etat0)
        inter = t.interval
        time += inter
        print(f'\ndurée du cyle {j+1}: {inter}\n')

    print(f'durée totale : {time} | durée par cycle : {time/cycles}')
    print(f'end at : {whatTimeIsIt()}')

