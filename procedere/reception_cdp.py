""" module de traitements des cdp """
import threading
from pathlib import Path
from datetime import datetime, timezone

from mflog import get_logger

from procedere import models as pm
from parameters import models as param
from helpers.gestion_dossier import GestionDossier
from carto import traitement_carto as tc 

def reception_cdp(dp):
    plat = TraitementsCdp(dp)
    plat.start()
    return True

def am_i_master():
    #TODO real one
    return True



class GestionCdp(GestionDossier):

    def __init__(self, cdp):
        self.logger = get_logger('GestionDossier')
        self.logger.debug(cdp.produit.name)
        self.cdp = cdp
        self.chemin = param.get_value('app', 'chemin_cdp')
        self.produit = self.cdp.produit.name
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
        self._path = Path(self.chemin, self.produit)

    def creer_fichier(self):
        return super().creer_fichier(self.cdp.name, self.cdp.data)


class TraitementsCdp(threading.Thread):
    logger = get_logger("thread traitement")

    def __init__(self, cdp, **kwargs):
        self.logger.debug("instanciation du thread")
        self.cdp = pm.produit.Cdp.create(cdp)
        super().__init__(**kwargs)

    def verif_reseau(self):
        now = datetime.now(timezone.utc)
        pass

    def sauv_local(self):
        gestion = GestionCdp(self.cdp)
        sortie = gestion.creer_fichier()
        return sortie
        

    # méthodes ci-dessous en static car on part d'une liste de cdp
    @staticmethod
    def carto(cdp):
        carto_process = tc.TraitementCarto(cdp)
        return carto_process.process()

    @staticmethod
    def get_list_cdp():
        # checker carto + diffusion
        
        return []

    @staticmethod
    def set_etats(cdp):
        pass

    @staticmethod
    def set_avertissements(cdp):
        pass

    @staticmethod
    def set_diffusions(cdp):
        pass


    def run(self):
        self.logger.debug("démarrage du traitement")
        self.logger.debug("vérifications")
        if self.cdp == None :
            self.logger.warning("cdp mal formé")
            return None
        if self.verif_reseau() == False :
            self.logger.info("réseau en retard déjà instancié à -1")
            return None
        if self.sauv_local() == False:
            self.logger.warning("impossible de sauvegarder un cdp !\
                         cdp {cdp.reseau} du produit {cdp.produit_id}")
            return None
        else :
            self.logger.info(f"cdp {self.cdp.name} sauvegardé")
        if am_i_master() == False:
            self.logger.info("cdp reçu et pris en charge - Sensei s'en occupe")
            return None

        self.logger.debug("démarrage de la boucle sur les cdp")
        cdp_list = self.get_list_cdp(self.cdp.produit_id)
        cdp_list.sort(key=lambda x: x.reseau)
        for cdp in cdp_list :
            self.logger.info(f'traitment cdp {cdp.reseau} du produit {cdp.produit_id}')
            if not cdp.statut_carto :
                try :
                    if self.carto(cdp) == True:
                        cdp.statut_carto = True
                        cdp.save()
                except :
                    self.logger.warning(f'carto de {cdp.reseau} du produit {cdp.produit_id} a échoué')
            if not cdp.statut_diffusions :
                if not am_i_master() :
                    break
                try :
                    if not cdp.statut_etats :
                        self.set_etats(cdp)
                except :
                    self.logger.warning(f'ETATS de {cdp.reseau} du produit {cdp.produit_id} a échoué')
                    return None
                if not am_i_master() :
                    break
                try :
                    if not cdp.statut_avertissements :
                        self.set_avertissements(cdp)
                except :
                    self.logger.warning(f'AVERTISSEMENTS de {cdp.reseau} du produit {cdp.produit_id} a échoué')
                #self.set_diffusions() !! à faire dans une autre requete

        return True

    