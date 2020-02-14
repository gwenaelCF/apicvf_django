""" module de traitements des cdp """
import time
import threading
import logging
from mflog import get_logger

from procedere import models as pm
#
# démarrage en cas de requête mfdata
class ReceptionCdp(threading.Thread):
    def __init__(self, cdp, **kwargs):
        self.cdp = cdp
        super(ReceptionCdp, self).__init__(**kwargs)

    def run(self):
        logger = get_logger("apicvf_django")
        logger.debug("démarrage du traitement")
        data = self.cdp.read()
        time.sleep(30)
        logger.debug(data)
        logger.debug("et voilà")


#fonctions de comparaison
def seuilCompar(x):
    """ règle de comparaison pour les seuils """
    # 0<-1<1<2
    return (2*(x**2)+x)

def findMax(l):
    """ trouver le seuil maximum """
    return max(set(l), key=seuilCompar)


def regles_vf(derniere_alerte, heure_reseau, t0, t_1, dt):
    """
     retourne True si une alerte de seuil t0 est diffusée

    derniere_alerte : object représentant la dernière alerte diffusée
    heure_reseau : heure du dernier reseau
    t0 : seuil du dernier réseau (en cours de traitement)
    t_1 : seuil de l'avant-dernier réseau (dernier traité)
    dt : paramètre de persistance des alertes (6 heures d'après la doc)
    
    """
    caduc = (derniere_alerte.time+dt) <= heure_reseau
    if  t0 in [1,2]:
        if t0 > derniere_alerte.seuil or caduc :
            return True
    if t0 == -1:
        if caduc and t_1 == -1:
            return True
    return False


def regl_apic_obj(obj):
    """ règle de diffusion pour les apic """
    t0 = obj.t0
    t_1 = obj.t_1
    t_2 = obj.t_2
    return regl_apic_seuils(t_2, t_1, t0)

def regl_apic_seuils(t_2,t_1,t0):
    """ règle de diffusion pour les apic """
    if t0:
        if t0==-1 :
            if (t_1==-1 and t_2 in [0,1]):
                return True
        if t_1<t0 :
            return True
    return False

# regles sous forme de dictionnaire !!! à mettre à jour
dico_cas_apic ={(-1, -1, -1): False, (-1, -1, 0): False, (-1, -1, 1): True, (-1, -1, 2): True, (-1, 0, -1): False, (-1, 0, 0): False, (-1, 0, 1): True, (-1, 0, 2): True, (-1, 1, -1): False, (-1, 1, 0): False, (-1, 1, 1): False, (-1, 1, 2): True, (-1, 2, -1): False, (-1, 2, 0): False, (-1, 2, 1): False, (-1, 2, 2): False, (0, -1, -1): True, (0, -1, 0): False, (0, -1, 1): True, (0, -1, 2): True, (0, 0, -1): False, (0, 0, 0): False, (0, 0, 1): True, (0, 0, 2): True, (0, 1, -1): False, (0, 1, 0): False, (0, 1, 1): False, (0, 1, 2): True, (0, 2, -1): False, (0, 2, 0): False, (0, 2, 1): False, (0, 2, 2): False, (1, -1, -1): True, (1, -1, 0): False, (1, -1, 1): False, (1, -1, 2): True, (1, 0, -1): False, (1, 0, 0): False, (1, 0, 1): True, (1, 0, 2): True, (1, 1, -1): False, (1, 1, 0): False, (1, 1, 1): False, (1, 1, 2): True, (1, 2, -1): False, (1, 2, 0): False, (1, 2, 1): False, (1, 2, 2): False, (2, -1, -1): False, (2, -1, 0): False, (2, -1, 1): False, (2, -1, 2): False, (2, 0, -1): False, (2, 0, 0): False, (2, 0, 1): True, (2, 0, 2): True, (2, 1, -1): False, (2, 1, 0): False, (2, 1, 1): False, (2, 1, 2): True, (2, 2, -1): False, (2, 2, 0): False, (2, 2, 1): False, (2, 2, 2): False}
dico_cas_vf ={(0, -1, -1): True, (1, -1, -1): True, (-1, -1, -1): False, (2, -1, -1): False, (-1, 0, -1): False, (0, 0, -1): False, (1, 0, -1): False, (2, 0, -1): False, (-1, 1, -1): False, (0, 1, -1): False, (1, 1, -1): False, (2, 1, -1): False, (-1, 2, -1): False, (0, 2, -1): False, (1, 2, -1): False, (2, 2, -1): False, (-1, -1, 0): False, (0, -1, 0): False, (1, -1, 0): False, (2, -1, 0): False, (-1, 0, 0): False, (0, 0, 0): False, (1, 0, 0): False, (2, 0, 0): False, (-1, 1, 0): False, (0, 1, 0): False, (1, 1, 0): False, (2, 1, 0): False, (-1, 2, 0): False, (0, 2, 0): False, (1, 2, 0): False, (2, 2, 0): False, (-1, -1, 1): True, (0, -1, 1): True, (1, -1, 1): False, (2, -1, 1): False, (-1, 0, 1): True, (0, 0, 1): True, (1, 0, 1): True, (2, 0, 1): True, (-1, 1, 1): False, (0, 1, 1): False, (1, 1, 1): False, (2, 1, 1): False, (-1, 2, 1): False, (0, 2, 1): False, (1, 2, 1): False, (2, 2, 1): False, (-1, -1, 2): True, (0, -1, 2): True, (1, -1, 2): True, (2, -1, 2): False, (-1, 0, 2): True, (0, 0, 2): True, (1, 0, 2): True, (2, 0, 2): True, (-1, 1, 2): True, (0, 1, 2): True, (1, 1, 2): True, (2, 1, 2): True, (-1, 2, 2): False, (0, 2, 2): False, (1, 2, 2): False, (2, 2, 2): False}

