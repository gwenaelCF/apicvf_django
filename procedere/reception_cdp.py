""" module de traitements des cdp """
import threading
import subprocess
import requests
from django.conf import settings
from pathlib import Path
from datetime import datetime, timezone, timedelta

from mflog import get_logger

from procedere import models as pm
from parameters import models as param
from procedere.utils import GestionCdp, create_cdp, modif_seuils_batch, findmax
from carto import traitement_carto as tc
from helpers import timing



def reception_cdp(dp):
    """
        démarrer le thread de traitement 
        en laissant la requête appelante se conclure
    """
    plat = TraitementsCdp(dp)
    plat.start()
    return True


def am_i_master():
    """
        vérification master (solution 1)
        - solution 1 (uuid): vérifie si local nginx uuid = virtual nginx uuid
        - solution 2 (ip_addr): vérifie si la commande 'ip addr' retourne
            l'adresse ip virtuelle en tant que 'scope global secondary ethX'
    """
    logger = get_logger("am_i_master")

    # ip/port virtual
    ip_addr = param.System.get_value('virtual_ip_middle')
    port = param.System.get_value('virtual_port_middle')

    # solution choice (from paramters)
    choice = param.System.get_value('check_master_mode')

    try:

        # 1. Solution uuid
        if choice == 'uuid':

            local_uuid_file = "default_uuid_local_file"
            local_uuid_http = "default_uuid_local_http"
            virtual_uuid = "default_uuid_remote"

            # Get local uuid from file /home/mfserv/var/uuid
            mfserv_local_path = param.System.get_value('mfserv_local_path')
            uuid_file_path = mfserv_local_path + '/var/uuid'
            with open(uuid_file_path, "r") as uuid_file:
                local_uuid_file = uuid_file.read().strip()
            logger.debug("local uuid file : " + local_uuid_file)

            # Get local uuid from http (ensure local server is OK)
            mfserv_local_port = param.System.get_value('mfserv_local_port')
            url = "http://localhost:{}/uuid".format(mfserv_local_port)
            resp = requests.get(url, timeout=10)
            local_uuid_http = resp.content.strip().decode()
            logger.debug("local uuid http : " + local_uuid_http)
            assert local_uuid_file == local_uuid_http, 'local server seems down'

            # Get uuid from virtual (proxy)
            url = "http://{}:{}/uuid".format(ip_addr, port)
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                virtual_uuid = response.content.strip().decode()
                logger.debug("remote uuid : " + virtual_uuid)
            else:
                logger.warning("impossible de joindre l'adresse virtuelle")

            # If local uuid = remote uuid, return True
            if virtual_uuid == local_uuid_http:
                logger.info("i am the master")
                return True

        # 2. Solution ip addr
        elif choice == 'ip_addr':

            command = ('/sbin/ip addr show dev {0} | grep "inet {1}" 2>/dev/null | wc -l'
                       .format(settings.NETWORK_INTERFACE, ip_addr))
            logger.debug(f"command : {command}")

            # Execute command
            ip_addr_return = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)

            # If virtual ip is found, return True
            if int(ip_addr_return) == 1:
                logger.info("i am the master")
                return True

        # Default, slave
        logger.warning("i am the slave")

    except Exception as exc:
        logger.error(exc, exc_info=True)
        return False

    # Default, slave
    return False

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
        if (self.cdp.reseau < self.reseau_courant
            ) and not self.cdp.name.endswith('.LATE'):
            return False
        return True

    def sauv_local(self):
        """
            sauvegarde et efface si plus de 72h
        """
        gestion = GestionCdp(self.cdp)
        reseau_text = self.cdp.reseau.strftime('%Y%m%d%H%M')
        self.logger.debug(
            f'{reseau_text}, {gestion.trouve_fichier(reseau_text)}'
        )
        if gestion.trouve_fichier(self.cdp.reseau.strftime('%Y%m%d%H%M')):
            self.logger.info(f'{self.cdp.name} déjà sauvegardé')
            return False
        sortie = gestion.creer_fichier()
        euthanasie = int(
            (self.cdp.reseau - timedelta(hours=72)).strftime('%Y%m%d%H%M'))
        for p in gestion.lister_fichiers():
            if int(p.stem) < euthanasie:
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
        reseau = self.reseau_courant - timedelta(minutes=30)
        while reseau >= self.reseau_courant - timedelta(hours=72):
            try:
                # cdp en base ?
                if pm.produit.Cdp.objects.filter(
                                    produit_id=self.cdp.produit_id, reseau=reseau
                                    ).exists():
                    cdp_prev = pm.produit.Cdp.objects.get(
                                        produit_id=self.cdp.produit_id,
                                        reseau=reseau
                                        )
                    self.logger.debug(f'{cdp_prev} en base')
                    if not cdp_prev.statut_carto or not cdp_prev.statut_diffusions:
                        cdp_a_traiter.append(cdp_prev)
                    else:
                        break
                # alors en local ?
                else:
                    gestion = GestionCdp(self.cdp)
                    if gestion.trouve_fichier(reseau.strftime('%Y%m%d%H%M')):
                        cdp_buffer = create_cdp(self.cdp.produit,
                                                reseau,
                                                cdp_file=gestion.path.joinpath(
                                                    reseau.strftime('%Y%m%d%H%M'))
                                                )
                        cdp_prev = pm.produit.Cdp.create(cdp_buffer)
                        self.logger.debug(f'{cdp_prev} en local')
                        if cdp_prev == None:
                            self.logger.warning(
                                f'cdp {reseau} du produit {self.cdp.produit.name} pas en base et impossible à créer'
                            )
                            break
                        cdp_prev.save()
                        cdp_a_traiter.append(cdp_prev)
                    # ni en base, ni local, on ne peut rien faire (pupitreurs ?)
                    else:
                        self.logger.warning(
                            f'cdp {reseau} du produit {self.cdp.produit.name} introuvable localement'
                        )
                        break
            except Exception as e:
                self.logger.warning(str(e))

            reseau -= timedelta(minutes=15)
        self.logger.debug([cdp.reseau for cdp in cdp_a_traiter])
        return cdp_a_traiter

    # méthodes ci-dessous en static/class car on part d'une liste de cdp
    @staticmethod
    def carto(cdp):
        """
            lance la carto
            très loin
        """
        carto_process = tc.TraitementCarto(cdp)
        return carto_process.process()

    @classmethod
    def set_etats(cls, cdp):
        seuils = {0: [], -1: [], 1: [], 2: []}
        with timing.Timer() as t:
            # update des EtatGrain
            cls.logger.debug(f'création dico des seuils de grains')
            qs_etat = pm.etat.EtatGrainProduit.objects.filter(
                                                    produit_id=cdp.produit_id)
            list_insee = list(qs_etat.values_list('grain__insee', flat=True))
            if cdp.retard:
                seuils[-1]=[insee for insee in list_insee]
            else:
                for insee, seuil in cdp.seuils_grains.items():
                    seuils[int(seuil)].append(insee)
                seuils[0]= set(list_insee).difference(cdp.seuils_grains.keys())
            cls.logger.debug(f'update (état)grains en base')
            for key in seuils.keys():
                modif_seuils_batch(qs_etat.filter(grain__insee__in=seuils[key]),
                                    key
                                    )
            pm.produit.Cdp.objects.filter(id=cdp.id).update(statut_etats=True)
            # update des EtatDept
            qs_etat_dept = pm.etat.EtatDeptProduit.objects.filter(
                                                    produit_id=cdp.produit_id)
            if cdp.retard:
                etat_dept_dict = {etat_dept.id: -1 for etat_dept in qs_etat_dept}
            else:
                etat_dept_dict = {etat_dept.id:findmax([
                    cdp.seuils_grains.get(x,0) 
                    for x in etat_dept.dept.grain_set.values_list('insee', flat=True)
                    ]) for etat_dept in qs_etat_dept}
            seuils_dept = {0: [], -1: [], 1: [], 2: []}
            for key, value in etat_dept_dict.items():
                seuils_dept[value].append(key)
            for key, value in seuils_dept.items():
                modif_seuils_batch(qs_etat_dept.filter(id__in=value),key)

        cls.logger.info(f'update etats fait en {t.interval}')

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
        self.logger= self.logger.bind(produit=self.cdp.produit.shortname, reseau=self.cdp.reseau)
        self.logger.debug("démarrage du traitement")
        self.logger.debug("vérifications")
        if self.cdp == None:
            self.logger.warning("cdp mal formé")
            return None
        dnow = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        self.cdp.reception = dnow
        self.reseau_courant = dnow - timedelta(minutes=dnow.minute % 15)
        if self.verif_reseau() == False:
            self.logger.warning("réseau en retard (déjà instancié à -1 ?)")
            #return None
        if self.sauv_local() == False:
            self.logger.warning(
                f"impossible de sauvegarder localement le cdp"
            )
            return None
        else:
            self.logger.info(f"cdp {self.cdp.name} sauvegardé localement")
        if am_i_master() == False:
            self.logger.info("cdp reçu et pris en charge - Sensei s'en occupe")
            return None
        try:
            self.cdp.save()
            self.logger.info(f"cdp {self.cdp.name} sauvegardé en base")
        except Exception as e:
            self.logger.warning(
                f'cdp {self.cdp.name} non sauvegardé en base !\n'+str(e))
        self.logger.debug("démarrage de la boucle sur les cdp")
        cdp_list = self.get_list_cdp()
        cdp_list.sort(key=lambda x: x.reseau)
        for cdp in cdp_list:
            self.logger.info(
                f'traitement cdp {cdp.reseau} du produit {cdp.produit_id}')
            if not cdp.statut_carto:
                try:
                    if self.carto(cdp) == True:
                        cdp.statut_carto = True
                        cdp.save()
                except Exception as e:
                    self.logger.warning(str(e))
                    self.logger.warning(
                        f'carto de {cdp.reseau} du produit {cdp.produit.shortname} a échoué')
            self.logger.debug(
                f'cdp.statut_diffusions: {cdp.statut_diffusions} | cdp.reseau {cdp.reseau} | reseau courant - 1h: {self.reseau_courant - timedelta(hours=1)}'
                )
            if (not cdp.statut_diffusions) and (
                    cdp.reseau >= self.reseau_courant - timedelta(hours=1)
                                        ) and am_i_master():
                if not cdp.statut_etats:
                    self.logger.debug(f"traitement ETATS")
                    self.set_etats(cdp)
                else:
                    self.logger.debug(f"déjà traité pr les états")
                if not am_i_master():
                    break
                if not cdp.statut_avertissements:
                    self.logger.debug(f"traitement AVERTISSEMENTS")
                    self.set_avertissements(cdp)
                if not cdp.statut_diffusions:
                    self.logger.debug(f"traitement DIFFUSIONS")
                    #self.set_diffusions() !! à faire dans une autre requete

        return True
