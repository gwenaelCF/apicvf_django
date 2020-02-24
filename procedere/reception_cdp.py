""" module de traitements des cdp """
import time
import threading
import logging
from mflog import get_logger

from procedere import models as pm
#
# démarrage en cas de requête mfdata
def reception_cdp(dp):
    # TODO créer réellement l'object cdp
    # TODO controle fichier reçu
    cdp = dp
    teg = TraitementEtatGrains(cdp)
    teg.start()
    tc = TraitementCarto(cdp)
    tc.start()
    return True

def am_i_master():
    #TODO real one
    return True
