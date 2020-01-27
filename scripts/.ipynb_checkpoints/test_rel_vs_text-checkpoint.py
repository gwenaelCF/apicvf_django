import random
import time

import testDB

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


def createGrain(nbGrain):
    with Timer() as t:
        for i in range(nbGrain):
            testDB.models.Grain.objects.create(id=i)
    print(f'grains:{t.interval}')

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

def testRl(nbCycles):
    print(f'test par relation base')
    print(time.time())
    with Timer() as t:
        for i in range(nbCycles):
            with Timer() as q:
                grains = testDB.models.Grain.objects.all()
                for grain in grains:
                    grain.seuil=random.randint(0,10)
                testDB.models.Grain.objects.bulk_update(grains,['seuil'])
            print(f'seuils grains màj {q.interval}')
            with Timer() as q :
                abos = testDB.models.Abo.objects.filter(grains__seuil__gte=8).distinct()
                for abo in abos:
                    abo.seuil = max(grain.seuil for grain in abo.grains.all())
                testDB.models.Abo.objects.bulk_update(abos,['seuil'])
            print(f'seuils abo màj {q.interval}')
            print(f'base {i+1}')
    print(f'relation base:{t.interval}')


def testText(nbCycles):
    print(f'test par relation text')
    print(time.time())
    with Timer() as t:
        for i in range(nbCycles):
            grains = testDB.models.Grain.objects.all()
            for grain in testDB.models.Grain.objects.all():
                grain.seuil=random.randint(0,10)
            testDB.models.Grain.objects.bulk_update(grains,['seuil'])
            grains = testDB.models.Grain.objects.filter(seuil__gte=8)
            for grain in grains :
                for abo in testDB.models.Abo.objects.filter(id__in=[
                    int(i) for i in grain.aboList.rstrip(',').split(',') if i!=''
                ]).distinct():
                    abo.seuil=grain.seuil
                    abo.save()
            print(f'texte {i+1}')
    print(f'{t.interval}')  
    

def armaged():
    print(f'remise à zéro')
    with Timer() as t:
        testDB.models.Abo.objects.all().delete()
        testDB.models.Grain.objects.all().delete()
    print(f'tables rasées:{t.interval}')

def run(nbAbo = 100000, nbGrain = 40000, nbGrainParAbo= 6, nbCycles = 100):
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