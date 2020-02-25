""" module de traitements des cdp """
import time
import threading

from mflog import get_logger

from procedere import models as pm
from helpers.gestion_dossier import GestionDossier

def reception_cdp(dp):
    plat = TraitementsCdp(dp)
    plat.start()
    return True

def am_i_master():
    #TODO real one
    return True

def carto(cdp):
    return False

def verif_reseau(cdp):
    pass

def sauv_local(data):
    pass

def get_list_cdp(cdp):
    # checker carto + diffusion
    # var cdp as a by-pass !! 2be removed
    return [cdp]

def set_etats(cdp):
    pass

def set_avertissements(cdp):
    pass

def set_diffusions(cdp):
    pass

class GestionCdp(GestionDossier):

    def __init__(self, chemincdp, nomproduit):
        
        self.chemin=chemincdp
        self.produit=nomproduit
        self.current = Path('.')
        self.path = Path(self.chemin, self.produit)
        self.creer_chemin()
        
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, p):
        if str(self.current.resolve().stem) in str(p.resolve()) :
            self.logger.error("le chemin de l'app est interdit")
            raise ValueError
        self._path = Path(chemin+produit)

class TraitementsCdp(threading.Thread):
    logger = get_logger("thread traitement")

    def __init__(self, cdp, **kwargs):
        self.logger.debug("instanciation du thread")
        self.cdp = pm.produit.Cdp.create(cdp)
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
        if sauv_local(self.cdp.data) == False:
            self.logger.warning("impossible de sauvegarder un cdp !\
                         cdp {cdp.reseau} du produit {cdp.produit_id}")
            return None
        if am_i_master() == False:
            self.logger.info("cdp reçu et pris en charge - Sensei s'en occupe")
            return None

        self.logger.debug("démarrage de la boucle sur les cdp")
        cdp_list = get_list_cdp(self.cdp)
        cdp_list.sort(key=lambda x: x.reseau)
        for cdp in cdp_list :
            #import carto quand l'app serait faite
            self.logger.info(f'traitment cdp {cdp.reseau} du produit {cdp.produit_id}')
            if not cdp.statut_carto :
                if carto(cdp) == True:
                    cdp.statut_carto = True
                    cdp.save()
            if not cdp.statut_diffusions :
                if not cdp.statut_etats :
                    set_etats(cdp)
                if not am_i_master() :
                    return None
                if not cdp.statut_avertissements :
                    set_avertissements(cdp)
                if not am_i_master():
                    return None
                
                set_diffusions(cdp)

        return True

    