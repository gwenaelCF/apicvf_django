import os
import csv
import time
import random

from apicvf.models import *


def seuil_compar(x):
    """ compare deux seuils selon la règle 0<-1<1<2 """
    return (2*(x**2)+x)

def findmax(l):
    """ max seuil liste sans 0 """
    return max(set(l), key=seuil_compar)


def findmax_z(l):
    """ max seuil liste avec 0 """
    l = set(l)
    l.remove(0)
    return max(l)

def regl_apic_obj(obj):
    t0 = obj.t0
    t_1 = obj.t_1
    t_2 = obj.t_2
    return regl_apic_seuils(t_2,t_1,t0)

def regl_apic_seuils(t_2,t_1,t0):
    if t0:
        if t0==-1:
            if t_1==-1 and t_2!=-1 and t_2!=2:
                return True
        elif t_1==-1:
            if t0>t_2 :
                return True
        elif t0>t_1 :
            return True
    return False

dico_cas_apic ={(-1, -1, -1): False, (-1, -1, 0): False, (-1, -1, 1): True, (-1, -1, 2): True, (-1, 0, -1): False, (-1, 0, 0): False, (-1, 0, 1): True, (-1, 0, 2): True, (-1, 1, -1): False, (-1, 1, 0): False, (-1, 1, 1): False, (-1, 1, 2): True, (-1, 2, -1): False, (-1, 2, 0): False, (-1, 2, 1): False, (-1, 2, 2): False, (0, -1, -1): True, (0, -1, 0): False, (0, -1, 1): True, (0, -1, 2): True, (0, 0, -1): False, (0, 0, 0): False, (0, 0, 1): True, (0, 0, 2): True, (0, 1, -1): False, (0, 1, 0): False, (0, 1, 1): False, (0, 1, 2): True, (0, 2, -1): False, (0, 2, 0): False, (0, 2, 1): False, (0, 2, 2): False, (1, -1, -1): True, (1, -1, 0): False, (1, -1, 1): False, (1, -1, 2): True, (1, 0, -1): False, (1, 0, 0): False, (1, 0, 1): True, (1, 0, 2): True, (1, 1, -1): False, (1, 1, 0): False, (1, 1, 1): False, (1, 1, 2): True, (1, 2, -1): False, (1, 2, 0): False, (1, 2, 1): False, (1, 2, 2): False, (2, -1, -1): False, (2, -1, 0): False, (2, -1, 1): False, (2, -1, 2): False, (2, 0, -1): False, (2, 0, 0): False, (2, 0, 1): True, (2, 0, 2): True, (2, 1, -1): False, (2, 1, 0): False, (2, 1, 1): False, (2, 1, 2): True, (2, 2, -1): False, (2, 2, 0): False, (2, 2, 1): False, (2, 2, 2): False}
dico_cas_vf ={(0, -1, -1): True, (1, -1, -1): True, (-1, -1, -1): False, (2, -1, -1): False, (-1, 0, -1): False, (0, 0, -1): False, (1, 0, -1): False, (2, 0, -1): False, (-1, 1, -1): False, (0, 1, -1): False, (1, 1, -1): False, (2, 1, -1): False, (-1, 2, -1): False, (0, 2, -1): False, (1, 2, -1): False, (2, 2, -1): False, (-1, -1, 0): False, (0, -1, 0): False, (1, -1, 0): False, (2, -1, 0): False, (-1, 0, 0): False, (0, 0, 0): False, (1, 0, 0): False, (2, 0, 0): False, (-1, 1, 0): False, (0, 1, 0): False, (1, 1, 0): False, (2, 1, 0): False, (-1, 2, 0): False, (0, 2, 0): False, (1, 2, 0): False, (2, 2, 0): False, (-1, -1, 1): True, (0, -1, 1): True, (1, -1, 1): False, (2, -1, 1): False, (-1, 0, 1): True, (0, 0, 1): True, (1, 0, 1): True, (2, 0, 1): True, (-1, 1, 1): False, (0, 1, 1): False, (1, 1, 1): False, (2, 1, 1): False, (-1, 2, 1): False, (0, 2, 1): False, (1, 2, 1): False, (2, 2, 1): False, (-1, -1, 2): True, (0, -1, 2): True, (1, -1, 2): True, (2, -1, 2): False, (-1, 0, 2): True, (0, 0, 2): True, (1, 0, 2): True, (2, 0, 2): True, (-1, 1, 2): True, (0, 1, 2): True, (1, 1, 2): True, (2, 1, 2): True, (-1, 2, 2): False, (0, 2, 2): False, (1, 2, 2): False, (2, 2, 2): False}


def regl_apic_list(t_2, t_1, t0):
    """ wahou """
    return dico_cas_apic[(t_2,t_1,t0)]



