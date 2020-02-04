import random
import time
from injectionCdP import models
from django.db.models import F

aboNat = 0
aboDep = 0
aboComCom = 70000


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
            del self.start_time # Force timer reinit  
  
# with Timer() as timer:  
#     content = call_server()  
#     result = process_data(content)  
# print 'Total time in seconds for first call:', timer.interval  



def run(*args):

    t0 = -1
    grain = 'grain' in args
    abo = 'abo' in args
    surv = 'surv' in args
    modif = 'modif' in args

    print(time.strftime("%A %d %B %Y %H:%M:%S"))

    with Timer() as globalTimer:
        if grain:
            print("\ncréation des communes")
            with Timer() as timer:
                count = createGrain()
            print(f"{count} communes créées en {timer.interval}")

        if abo:
            print("\ncréation des abonnements")
            with Timer() as timer:
                createAbo()
            print(f"{models.Abonnement.objects.count()} abonnements créées en {timer.interval}")
        
        if surv:        
            print("\ncréation des surveillances")
            with Timer() as timer:
                count=createSurveil()
            print(f"{count} surveillances faites en {timer.interval}")

        if modif:
            print("\nmodifications lancées")
            print(f"{models.Grain.objects.count()} grains et {models.Abonnement.objects.count()} abonnements en base")
            with Timer() as timer:
                countAbo, countComm=modifAll(t0)
            print(f"abonnements et communes modifiés en {timer.interval}")
    print(f"\nTout cela en {globalTimer.interval}")

    print('Fin ',time.strftime("%A %d %B %Y %H:%M:%S"))

def modifEtat(etat, t0):
    newEtat = {
                't-2':etat['t-1'],
                't-1':etat['t0'],
                't0':t0,
                }
    return newEtat

def createGrain():
    count = 0
    with open('comsimp2016.txt','r',errors='ignore') as f:
        f.readline()
        lin = f.readline()
        while lin:
            liste=lin.split('\t')
            comDep = liste[4]
            comNum = liste[5].rjust(3,'0')
            comName = liste[9]
            newCom = models.Grain(insee=comDep+comNum, dep=comDep, metrop=(int(comDep)<100))
            newCom.save()
            count+=1
            lin=f.readline()
    return count

def createAbo():
    print(f'création de {aboNat} abo nationaux, de {aboDep} abo départementaux et de {aboComCom} abo zones de communes')
    
    empNat = {'nat':True}

    for _ in range(aboNat):
        newAbo = models.Abonnement(emprise=empNat)
        newAbo.save()
    
    for _ in range(aboDep):
        empDep = str(random.randint(1,95)).rjust(3,'0')
        newAbo = models.Abonnement(emprise={'dep':empDep})
        newAbo.save()

    for _ in range(aboComCom):
        newAbo = models.Abonnement(emprise={'com':[]})
        for i in range(random.randint(4, 12)):
            com = models.Grain.objects.get(id=random.randint(1,35000))
            newAbo.emprise['com']+=[com.insee]
        newAbo.save()

def createSurveil():
    count=0
    for abo in models.Abonnement.objects.all():
        if 'nat' in abo.emprise and abo.emprise['nat'] == True:
            communes = models.Grain.objects.filter(metrop=True)
        elif abo.emprise.get('dep',False):
            communes = models.Grain.objects.filter(dep=abo.emprise['dep'])
        else :
            communes = models.Grain.objects.filter(insee__in=abo.emprise['com'])

        for comm in communes:
            newSurv = models.Surveillance(abonnement=abo, grain=comm)
            newSurv.save()
            count+=1

    return count

def modifAll(t0):
    countAbo, countComm = 0, 0
    for abo in models.Abonnement.objects.all():
        oldEtat = abo.etat
        abo.etat = modifEtat(oldEtat, t0)
        abo.save()
        countAbo+=1
    for grain in models.Grain.objects.all():
        oldEtat = grain.etat
        grain.etat = modifEtat(oldEtat, t0)
        grain.save()
        countComm+=1
    return countAbo, countComm


