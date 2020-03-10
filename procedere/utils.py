from pathlib import Path
from datetime import datetime, timedelta, timezone

from django.db.models import F
from mflog import get_logger

from helpers.gestion_dossier import GestionDossier
from parameters import models as param

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

from procedere.models import produit, granularite, etat


class GestionCdp(GestionDossier):
    """
        utilitaire de gestion des fichiers cdp en local
    """

    def __init__(self, cdp):
        self.logger = get_logger('GestionDossier')
        self.logger.debug(f'produit: {cdp.produit.name}')
        self.cdp = cdp
        self.chemin = param.get_value('app', 'chemin_cdp')
        self.produit = self.cdp.produit.shortname
        self.current = Path('.')
        self.path = Path(self.chemin, self.produit)
        self.creer_chemin()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, p):
        # if str(self.current.resolve().stem) in str(p.resolve()) :
        #    self.logger.error("le chemin de l'app est interdit")
        #    raise ValueError
        self._path = Path(self.chemin, self.produit)

    def creer_fichier(self):
        return super().creer_fichier(self.cdp.reseau.strftime('%Y%m%d%H%M'), self.cdp.brut)


def create_cdp(prod, reseau, cdp_file=None):
    """
        renvoie un cdp comme uploadé

        prod -- produit désiré
        reseau -- heure du réseau
        cdp_file -- Path 
                    si None, tout à seuil=-1, 
                    sinon les données viennent du fichier
    """
    logger = get_logger('create_cdp')
    reception = (reseau+timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')
    reseau = reseau.strftime('%Y%m%d%H%M')

    
    if not cdp_file:
        name = prod.entete + '_' + reseau[6:] + \
        '.' + reception + '_XXXXXXXXXXX_XXXXX.XXX.LT' + '.LATE'
        liste_insee = granularite.Grain.objects.filter(
            id__in=prod.etatgrainproduit_set.values_list('grain_id', flat=True)
        ).values_list('insee', flat=True)
        # TODO revoir le format en fonction des choix definitifs pour les CDP
        troncons = ';0;' if prod.shortname.startswith('V') else ';'
        texte = bytes(reseau+troncons+str(len(liste_insee))+'\n', 'UTF-8')
        logger.info(texte)
        forma = ';' if prod.shortname.startswith('V') else ';;;'
        for i in liste_insee:
            texte += bytes(i+forma+'-1\n', 'UTF-8')
    else:
        texte = open(cdp_file, 'rb').read()
    brut = BytesIO(texte)
    return InMemoryUploadedFile(brut,
                                None, name,
                                '_io.BytesIO', brut.__sizeof__(),
                                'UTF-8')


#
# update états
def modif_seuils_batch(qs, newt0):
    """ modifie une query_set (un ensemble de lignes) en base """
    up_kwargs = {'t_2': F('t_1'), 't_1': F('t0'), 't0': newt0}
    return qs.update(**up_kwargs)


def modif_seuil_unit(obj, newT0):
    """ modif l'objet pas la base (call obj.save() when needed) """
    obj.t_2 = obj.t_1
    obj.t_1 = obj.t0
    obj.t0 = int(newT0)
    return obj

# fonctions de comparaison


def compar_seuil(x):
    """ règle de comparaison pour les seuils """
    # 0<-1<1<2
    return (2*(x**2)+x)


def findmax(l):
    """ trouver le seuil maximum """
    return max(set(l), key=compar_seuil)


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
    if t0 in [1, 2]:
        if t0 > derniere_alerte.seuil or caduc:
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


def regl_apic_seuils(t_2, t_1, t0):
    """ règle de diffusion pour les apic """
    if t0:
        if t0 == -1:
            if (t_1 == -1 and t_2 in [0, 1]):
                return True
        if t_1 < t0:
            return True
    return False


# regles sous forme de dictionnaire !!! à mettre à jour
dico_cas_apic = {(-1, -1, -1): False, (-1, -1, 0): False, (-1, -1, 1): True, (-1, -1, 2): True, (-1, 0, -1): False, (-1, 0, 0): False, (-1, 0, 1): True, (-1, 0, 2): True, (-1, 1, -1): False, (-1, 1, 0): False, (-1, 1, 1): False, (-1, 1, 2): True, (-1, 2, -1): False, (-1, 2, 0): False, (-1, 2, 1): False, (-1, 2, 2): False, (0, -1, -1): True, (0, -1, 0): False, (0, -1, 1): True, (0, -1, 2): True, (0, 0, -1): False, (0, 0, 0): False, (0, 0, 1): True, (0, 0, 2): True, (0, 1, -1): False, (0, 1, 0): False, (0, 1, 1): False, (0, 1, 2): True, (0, 2, -1): False, (0, 2, 0): False, (0, 2, 1): False, (0, 2, 2)                 : False, (1, -1, -1): True, (1, -1, 0): False, (1, -1, 1): False, (1, -1, 2): True, (1, 0, -1): False, (1, 0, 0): False, (1, 0, 1): True, (1, 0, 2): True, (1, 1, -1): False, (1, 1, 0): False, (1, 1, 1): False, (1, 1, 2): True, (1, 2, -1): False, (1, 2, 0): False, (1, 2, 1): False, (1, 2, 2): False, (2, -1, -1): False, (2, -1, 0): False, (2, -1, 1): False, (2, -1, 2): False, (2, 0, -1): False, (2, 0, 0): False, (2, 0, 1): True, (2, 0, 2): True, (2, 1, -1): False, (2, 1, 0): False, (2, 1, 1): False, (2, 1, 2): True, (2, 2, -1): False, (2, 2, 0): False, (2, 2, 1): False, (2, 2, 2): False}
dico_cas_vf = {(0, -1, -1): True, (1, -1, -1): True, (-1, -1, -1): False, (2, -1, -1): False, (-1, 0, -1): False, (0, 0, -1): False, (1, 0, -1): False, (2, 0, -1): False, (-1, 1, -1): False, (0, 1, -1): False, (1, 1, -1): False, (2, 1, -1): False, (-1, 2, -1): False, (0, 2, -1): False, (1, 2, -1): False, (2, 2, -1): False, (-1, -1, 0): False, (0, -1, 0): False, (1, -1, 0): False, (2, -1, 0): False, (-1, 0, 0): False, (0, 0, 0): False, (1, 0, 0): False, (2, 0, 0): False, (-1, 1, 0): False, (0, 1, 0): False, (1, 1, 0): False, (2, 1, 0): False, (-1, 2, 0): False, (0, 2, 0): False, (1, 2, 0): False,
               (2, 2, 0): False, (-1, -1, 1): True, (0, -1, 1): True, (1, -1, 1): False, (2, -1, 1): False, (-1, 0, 1): True, (0, 0, 1): True, (1, 0, 1): True, (2, 0, 1): True, (-1, 1, 1): False, (0, 1, 1): False, (1, 1, 1): False, (2, 1, 1): False, (-1, 2, 1): False, (0, 2, 1): False, (1, 2, 1): False, (2, 2, 1): False, (-1, -1, 2): True, (0, -1, 2): True, (1, -1, 2): True, (2, -1, 2): False, (-1, 0, 2): True, (0, 0, 2): True, (1, 0, 2): True, (2, 0, 2): True, (-1, 1, 2): True, (0, 1, 2): True, (1, 1, 2): True, (2, 1, 2): True, (-1, 2, 2): False, (0, 2, 2): False, (1, 2, 2): False, (2, 2, 2): False}
