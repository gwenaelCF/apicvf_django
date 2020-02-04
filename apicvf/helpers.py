import time
import random

from django.db.models import Max, Min, F


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
    """ règle de comparaison pour les seuils """
    # 0<-1<1<2
    return (2*(x**2)+x)

def findMax(l):
    """ trouver le seuil maximum """
    return max(set(l), key=seuilCompar)

def regl_apic_obj(obj):
    """ règle de diffusion pour les apic """
    t0 = obj.t0
    t_1 = obj.t_1
    t_2 = obj.t_2
    return regl_apic_seuils(t_2, t_1, t0)

def regl_apic_seuils(t_2,t_1,t0):
    """ règle de diffusion pour les apic """
    if t0:
        if (t0==-1 and t_1==-1 and t_2!=-1):
            return True
        if (t0!=-1 and t_1==0) or t0>max(t_2,t_1):
            return True
    return False
#
#update en base
def modifSeuilBatch(qs, newt0):
    """ modifie une query_set (un ensemble de lignes en base) """
    up_kwargs = {'t_2':F('t_1'), 't_1':F('t0'), 't0':newt0}
    return qs.update(**up_kwargs)

def modifSeuilUnit(obj, newT0):
    """modif l'objet pas la base si .save() est commenté"""
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    return obj