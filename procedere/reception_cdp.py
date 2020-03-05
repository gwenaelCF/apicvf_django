""" module de traitements des cdp """
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta

from mflog import get_logger

from procedere import models as pm
#from parameters import models as param
from procedere.utils import GestionCdp
from carto import traitement_carto as tc 

def reception_cdp(dp):
    """
        démarrer le thread de traitement 
        en laissant la requête appelante se conclure
    """
    plat = TraitementsCdp(dp)
    plat.start()
    return True

def am_i_master():
    #TODO real one - à basculer en util ?
    return True

class TraitementsCdp(threading.Thread):
    """
        traitement carto et diffusion dans un thread dédié
        initiée par un cdp
    """
    logger = get_logger("thread traitement")
    def __init__(self, cdp, **kwargs):
        self.logger.debug("instanciation du thread")
        self.cdp = pm.produit.Cdp.create(cdp)
        super().__init__(**kwargs)

    def verif_reseau(self):
        if self.cdp.reseau < self.reseau_courant :
            return False
        return True

    def sauv_local(self):
        """
            sauvegarde et efface si plus de 72h
        """
        gestion = GestionCdp(self.cdp)
        if list(gestion.trouve_fichier(self.cdp.reseau.strftime('%Y%m%d%H%M'))):
            self.logger.info(f'{self.cdp.name} déjà sauvegardé')
            return False
        sortie = gestion.creer_fichier()
        euthanasie = int((self.cdp.reseau - timedelta(hours=72)).strftime('%Y%m%d%H%M'))
        for p in gestion.lister_fichiers():
            if int(p.stem)<euthanasie:
                gestion.efface_moissa(nom=p.stem)
        return sortie
        
    def get_list_cdp(self):
        """
            articulation en les cdp non traités (d'après la base)
            et les cdp dans le répertoire local
        """
        # checker carto + diffusion
        # param vf et apic ?
        cdp_a_traiter = [self.cdp]
        reseau = self.reseau_courant - timedelta(minutes=15)
        while reseau >= self.reseau_courant - timedelta(hours=72):
            try:
                if pm.produit.Cdp.objects.filter(
                                                produit_id=self.cdp.produit_id,
                                                reseau=reseau
                                                ).exists():
                    cdp_prev = pm.produit.Cdp.objects.get(
                                                produit_id=self.cdp.produit_id,
                                                reseau=reseau
                                                )
                else :
                    pass
                    self.logger.info(
                        f'cdp {reseau} du produit {self.cdp.produit.name} introuvable en base'
                        )
                    

            except Exception as e :            
                self.logger.warning(str(e))

            reseau -= timedelta(minutes=15)


        return cdp_a_traiter

    # méthodes ci-dessous en static car on part d'une liste de cdp
    @staticmethod
    def carto(cdp):
        carto_process = tc.TraitementCarto(cdp)
        return carto_process.process()

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
        """
            fonction lancée en thread pour traiter le cdp arrivant 
            et si besoin les cdp précédents
        """
        self.logger.debug("démarrage du traitement")
        self.logger.debug("vérifications")
        if self.cdp == None :
            self.logger.warning("cdp mal formé")
            return None
        dnow = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        self.cdp.reception = dnow
        self.reseau_courant = dnow - timedelta(minutes=dnow.minute %15)
        if self.verif_reseau() == False :
            self.logger.info("réseau en retard (déjà instancié à -1 ?)")
            #return None ## décommenter cette ligne pour sortir du débug
        if self.sauv_local() == False:
            self.logger.warning(
                f"impossible de sauvegarder localement le cdp {self.cdp.reseau} du produit {self.cdp.produit.shortname}"
                )
            return None
        else :
            self.logger.info(f"cdp {self.cdp.name} sauvegardé localement")
        if am_i_master() == False:
            self.logger.info("cdp reçu et pris en charge - Sensei s'en occupe")
            return None
        try :
            self.cdp.save()
            self.logger.info(f"cdp {self.cdp.name} sauvegardé en base")
        except Exception as e:
            self.logger.warning("cdp {self.cdp.name} non sauvegardé en base !\n"+str(e))
        self.logger.debug("démarrage de la boucle sur les cdp")
        cdp_list = self.get_list_cdp()
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
            if (not cdp.statut_diffusions) and (
                    cdp.reseau > self.reseau_courant - timedelta(hours=1)):
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

    