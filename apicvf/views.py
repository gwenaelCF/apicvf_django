''' vues pour test, fonctions à réinjecter par vues, règles métiers, helpers'''

import itertools
import csv
import time

from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import JsonResponse
#from django.template import loader
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.db.models import F, Count, Value as V
from django.template.loader import render_to_string

from .models import *
from cdp.models import *

import apicvf


class Timer(object):
    '''helper to be thrown in helpers file'''  
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




def index(request):
    return HttpResponse("Hello World from django app injectionCdP.")



def countBase():
    grain = Grain.objects.count()
    abo = Abonnement.objects.count()
    surv = Abonnement.objects.all().aggregate(Count('emprise_grain'))['emprise_grain__count']\
        +Abonnement.objects.all().aggregate(Count('emprise_dept'))['emprise_dept__count']
    dep = Dept.objects.count()

    return grain, abo, surv, dep

def namesBatchCdP():
    return [batch.name for batch in BatchCdp.objects.all()]


def seuilCompar(x):
    # 0<-1<1<2
    return (2*(x**2)+x)

def findMax(l):
    return max(set(l), key=seuilCompar)


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

def modifSeuilBatch(obj, t0):
    obj.update(t_2=F('t_1'))
    obj.update(t_1=F('t0'))
    obj.update(t0=int(t0))    

def modifSeuilUnit(obj, newT0):
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    obj.save()
    return obj

def modifEtatGrainProdBatch(dicoGrain):
    obj = EtatGrainProduit.objects.all()
    obj.update(t_2=F('t_1'))
    obj.update(t_1=F('t0'))
    obj.update(t0=dicoGrain.get(F('grain'), 0))

def modifEtatDeptProdBatch(dicoObj):
    etat = EtatDeptProduit.objects.all()
    etat.update(t_2=F('t_1'))
    etat.update(t_1=F('t0'))
    etat.update(t0=V(dicoObj.get(F('dept'), (0,))[0]))

def modifSeuil(obj, reseau, valeur=0):
    try :
        setattr(obj, reseau, valeur)
    except :
        pass


def reinitValid(data, valeur = 0):
    allObj = ['EtatGrainProduit','Abonnement','EtatDeptProduit']
    objName = int(data['reinitObject'])
    if objName != -1:
        allObj=[allObj[objName]]
    allSeuil = ['t0', 't_1', 't_2']
    seuilName = int(data['reinitSeuil'])
    if seuilName != -1:
        allSeuil = [allSeuil[seuilName]]
    for obj in allObj:
        for seuil in allSeuil:
            kwargs = {seuil:valeur}
            objAModif = getattr(injectionCdP.models, obj)
            objAModif.objects.update(**kwargs)

def inject(cdp):
    #pas beau, à voir pour améliorer les qs
    qs = EtatGrainProduit.objects.all()
    aModifCdP = qs.filter(grain__insee__in=cdp.grains.keys())
    aModif0 = qs.exclude(grain__insee__in=cdp.grains.keys())
    modifSeuilBatch(aModif0,0)
    etatGrainAverti = []
    deptModifCdp = {}
    for etat in aModifCdP:
        etat = modifSeuilUnit(etat, cdp.grains[etat.grain.insee])
        if reglApic(etat):
            etatGrainAverti.append(etat)
            deptModifCdp[etat.grain.dept] = deptModifCdp.get(etat.grain.dept, [])+[etat]
    
    #dept a modif (nouveau seuil, [grains concernés])
    etatDeptAverti ={}
    for dept in deptModifCdp.keys():
        seuilMax = findMax((etat.t0 for etat in deptModifCdp[dept]))
        etatD = modifSeuilUnit(EtatDeptProduit.objects.get(dept=dept), seuilMax)
        etatDeptAverti[etatD]=(seuilMax,[etatG for etatG in deptModifCdp[dept] if etatG.t0==seuilMax])

    return etatGrainAverti, etatDeptAverti

def avertirAboNat(depts):
    pass

def avertirAboDepts(etatDepts):
    # !!! inclure Produits !!!
    return [etatDept for etatDept in etatDepts if reglApic(etatDept)]


def avertirRl(etatGrains, etatDepts):
    aboAvList = []
    deptsAv = avertirAboDepts(etatDepts)
    if deptsAv:
        aboAvList.extend([(abo.id,'nat',deptsAv) for abo in Abonnement.objects.filter(emprise_nat=True)])
    #marche avec un seul dept par emprise, !!! VERIF avec plusieurs !!!
        aboAvList.extend([(abo.id,'dept',[etatD.dept.insee for etatD in deptsAv]) for abo in Abonnement.objects.filter(emprise_dept__in=[etatD.dept for etatD in etatDepts])])
    #revoir avec prise en compe histo abonnement !!!
    #grainsAv = [etatG.grain for etatG in etatGrains]
    #aboAvList.extend([(abo.id,'grains',abo.emprise_grain.all()) for abo in Abonnement.objects.all() if not set.isdisjoint(set(abo.emprise_grain.all()),set(grainsAv))])
    return aboAvList

def avertirText(grains, depts):
    pass



class TestView(View):

    def get(self, request):
        g, a, s, d = countBase()
        context = {
            'nb_grains': g,
            'nb_abo' : a,
            'nb_surv' : s,
            'nb_dep' : d,
            'batches': namesBatchCdP()
        }
        return render(request, 'injectionCdP/testing.html', context)

    def post(self, request):
        data = request.POST
        
        if 'flush' in data:
            Surveillance.objects.all().delete()
            #Abonnement.objects.all().delete()
            #Grain.objects.all().delete()
            messages.success(request, 'et pouf !')
        elif 'injectCdP' in data :
            return Injecting().post(request)
        elif 'reinitValid' in data :
            reinitValid(data)
            messages.success(request, data)
        return redirect('./testCdP')


def geneForStream(batchName, testType):
    timestamp, nbrCom, comAv, aboAv, localTime, globalTime = [],[],[],[],[],[]
    with Timer() as globalTimer:
        for c in CdpApic.objects.filter(batch_id__exact=batchName):
            with Timer() as localTimer:
                timestamp.append(c.dt)
                nbrCom.append(len(c.grains))
                grainAverti, deptAverti = inject(c)
                comAv.append(len(grainAverti))
                #a changer pour tests !!!
                if testType == 'Rl':
                    aboAv.append(avertirRl(grainAverti, deptAverti.keys()))
                elif testType == 'Text':
                    aboAv.append(avertirText(grainAverti,deptAverti.keys()))
            localTime.append(localTimer.interval)
    globalTime.append(globalTimer.interval)
    return timestamp, nbrCom, comAv, aboAv, localTime, globalTime

def streamHttp(request):
    tpl = render_to_string('injectionCdP/injecting.html', request=request)
    wraps = tpl.split('!!!DATA HERE!!!')
    timestamp, nbrCom, comAv, aboAv, localTime, globalTime = geneForStream(request.POST['injection'], request.POST['injectionType'])
    gene = [f'<tr><th scope=\"row\">{timestamp[i]}\
    </th><td>{nbrCom[i]}\
    </td><td>{comAv[i]}\
    </td><td>{aboAv[i]}\
    </td><td>{localTime[i]}\
    </td><td>{globalTime}ms\
    </td></tr>' for i in range(len(timestamp))]
    
    content = itertools.chain(wraps[0:1], gene, wraps[1:])

    return StreamingHttpResponse(content)

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def streamCSV(request):
    rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename"'
    return response

class Injecting(View):
    #pass
    def post(self, request):
        return streamHttp(request)