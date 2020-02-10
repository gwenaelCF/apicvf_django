from django.db.models import F

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
    return Fallse

#
#update états
def modifSeuilBatch(qs, newt0):
    """ modifie une query_set (un ensemble de lignes) en base """
    up_kwargs = {'t_2':F('t_1'), 't_1':F('t0'), 't0':newt0}
    return qs.update(**up_kwargs)

def modifSeuilUnit(obj, newT0):
    """ modif l'objet pas la base (call obj.save() when needed) """
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    return obj