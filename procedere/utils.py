from django.db.models import F


#
#update états
def modif_seuils_batch(qs, newt0):
    """ modifie une query_set (un ensemble de lignes) en base """
    up_kwargs = {'t_2':F('t_1'), 't_1':F('t0'), 't0':newt0}
    return qs.update(**up_kwargs)

def modif_seuil_unit(obj, newT0):
    """ modif l'objet pas la base (call obj.save() when needed) """
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    return obj