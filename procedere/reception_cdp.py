""" module de traitements des cdp """
import time
import threading
import logging
from mflog import get_logger

from procedere import models as pm
from . import traitement_etats_grains, traitement_carto
#
# démarrage en cas de requête mfdata
def reception_cdp(dp):
    # TODO créer réellement l'object cdp
    # TODO controle fichier reçu
    cdp = dp
    teg = traitement_etats_grains.TraitementEtatGrains(cdp)
    teg.start()
    tc = traitement_carto.TraitementCarto(cdp)
    tc.start()
    return True

def am_i_master():
    #TODO real one
    return True
