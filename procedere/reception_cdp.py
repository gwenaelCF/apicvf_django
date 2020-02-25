""" module de traitements des cdp """
import time
import threading
import logging
from mflog import get_logger

from procedere import models as pm
from . import traitement_etats_grains, traitement_carto
#
# démarrage en cas de requête mfdata
def reception_cdp(dp):l
    plat = TraitementsCdp(dp)
    plat.start()
    return True

def am_i_master():
    #TODO real one
    return True

class TraitementsCdp(threading.Thread):
    logger = get_logger("apicvf_django")

    def __init__(self, cdp, **kwargs):
        self.logger.debug("instanciation du thread")
        self.cdp = pm.produit.Cdp(cdp)
        super().__init__(**kwargs)

    def run(self):
        self.logger.debug("démarrage du traitement")
        self.logger.debug("vérifications")
        if self.cdp == None :
            self.logger.warning("cdp mal formé")
            return None
        if verif_reseau(self.cdp.reseau) == False :
            self.logger.info("réseau en retard déjà instancié à -1")
            return None
        if sauv_local(cdp.data) == False:
            self.logger.warning("impossible de sauvegarder un cdp !\
                         cdp {cdp.reseau} du produit {cdp.produit_id}")
            return None
        if am_i_master() == False:
            self.logger.info("cdp reçu et pris en charge - Sensei s'en occupe")
            return None

        self.logger.debug("démarrage de la boucle sur les cdp")
        cdp_list = get_list_cdp()
        cdp_list.sort(key=lambda x: x.reseau)
        for cdp in cdp_list :
            #import carto quand l'app serait faite
            self.logger.info(f'traitment cdp {cdp.reseau} du produit {cdp.produit_id}')
            if carto(cdp) == True:
                cdp.status_carto = True
                cdp.save()
            if cdp.status_etats == False :
                set_etats(cdp)
            if not am_i_master() :
                return None
            if not cdp.status_avertissements :
                set_avertissements(cdp)
            if not am_i_master():
                return None
            if not cdp.status_diffusions :
                set_diffusions(cdp)

        return True

    def verif_reseau(cdp):
        pass

    def sauv_local(data):
        pass

    def get_list_cdp():
        pass

    def set_etats(cdp):
        pass

    def set_avertissements(cdp):
        pass

    def set_diffusions(cdp):
        pass