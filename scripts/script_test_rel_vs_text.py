import random
import time

import testDB

from django.db.models import Max, Subquery, OuterRef

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
# initialisation
def armaged():
    print(f'remise à zéro')
    with Timer() as t:
        testDB.models.Abo.objects.all().delete()
        testDB.models.Grain.objects.all().delete()
    print(f'tables rasées:{t.interval}')

def createGrain(nbGrain):
    with Timer() as t:
        for i in range(nbGrain):
            testDB.models.Grain.objects.create(id=i)
    print(f'création grains:{t.interval}')

def createAbo(nbAbo, nbGrain, nbGrainParAbo):
        with Timer() as t:
            for i in range(nbAbo):
                abo = testDB.models.Abo.objects.create(id=i)
                g = random.sample(range(nbGrain), nbGrainParAbo)
                abo.grains.set(g)
                #abo.save()
                for grain in abo.grains.all():
                    grain.aboList = grain.aboList +str(abo.id)+','
                    grain.save()
        print(f'abo:{t.interval}')


#
# tests

# simulation arrivée de données
def randUpdateGrains(nbGrain):
    print(f'génération de nouveaux seuils grains')
    with Timer() as q:
        nvSeuils = random.choices([0,-1,1,2], cum_weights=[979, 989, 999, 1000], k=nbGrain)
    print(f'seuils grains générés {q.interval}')
    return nvSeuils

# test en BDD relationnelle
def testRl(nbCycles, nbGrain):
    print(f'test relationnelle')
    print(whatTimeIsIt())
    with Timer() as t:
        for i in range(nbCycles):
            print(f'cycle (base) n°{i+1}')
            nvSeuils = randUpdateGrains(nbGrain)
            grain1 = [i for i, value in enumerate(nvSeuils) if value==1]
            with Timer() as q :
                testDB.models.Abo.objects.update(seuil=Subquery(
                    testDB.models.Abo.objects.filter(
                        id=OuterRef('pk')).annotate(
                        maxSeuil=Max('grains__seuil')).values('maxSeuil')
                        ))
            print(f'seuils abo màj {q.interval}')
            
    print(f'relation base:{t.interval}')
    print(whatTimeIsIt())

# test en BDD descriptive
def testText(nbCycles, nbGrain):
    print(f'test texte')
    print(whatTimeIsIt())
    with Timer() as t:
        for i in range(nbCycles):
            print(f'cycle (texte) n°{i+1}')
            randUpdateGrains()
            with Timer() as q :
                grains = testDB.models.Grain.objects.filter(seuil__gte=8)
                for grain in grains :
                    for abo in testDB.models.Abo.objects.filter(id__in=[
                        int(i) for i in grain.aboList.rstrip(',').split(',') if i!=''
                    ]).distinct():
                        abo.seuil=grain.seuil
                        abo.save()
            print(f'seuils abo màj {q.interval}')
            
    print(f'{t.interval}')
    print(whatTimeIsIt())
    

# main
def run(nbAbo = 100000, nbGrain = 40000, nbGrainParAbo= 6, nbCycles = 1):
    #effacer
    #armaged()
    print(f'rappel des param:\nabo={nbAbo}, grains={nbGrain}, Grains par abo={nbGrainParAbo}, cycles={nbCycles}')
    print(f'mise en place des param')
    #créer
    #createGrain(nbGrain)
    #createAbo(nbAbo, nbGrain, nbGrainParAbo)
    
    #tester
    print(f'prêt')
    testRl(nbCycles)
    testText(nbCycles)
    
    print(f'touti va bene')