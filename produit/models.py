from datetime import datetime, timezone
import re

from django.db import models
from django.contrib.postgres.fields import JSONField

from mflog import get_logger
from procedere.models import etat, granularite

PRODUITS = {
    'AFR': 'APIC METROPOLE',
    'VFR': 'VF METROPOLE',
    'AAG': 'APIC ANTILLES GUYANE',
    'AOI': 'APIC OCEAN INDIEN',
    'ANC': 'APIC NOUVELLE CALEDONIE',
}

COUVERTURE_PRODUITS = {
    'fr': ['AFR', 'VFR'],
    'ga': ['AAG'],
    'ma': ['AAG'],
    're': ['AOI'],
    'nc': ['ANC']
}

PRODUITS_ORIGIN = {
    'AFR': ['fr'],
    'VFR': ['fr'],
    'AAG': ['ga', 'ma'],
    'AOI': ['re'],
    'ANC': ['nc']
}

ENTETES_PRODUITS = {
    'CDPC40_LFPW': 'VFR',
    'FPFR42_ATOS': 'AFR',
    'FPFR43_FMEE': 'AOI',
    'FPFR43_NWBB': 'ANC',
    'FPFR43_TFFF': 'AAG',
}

TIMEZONE = {
    'VFR': "Europe/Paris",
    'AFR': "Europe/Paris",
    'AOI': "Indian/Reunion",
    'ANC': "Pacific/Noumea",
    'AAG': "America/Guadeloupe"
}

logger = get_logger("produit (models)")


class Regle(models.Model):
    """ regle de calcul des avertissements
        fourni un JSON => dict() qui pour chaque clé renvoie True ou False pour diffusion
    """
    name = models.CharField(max_length=40, null=True, unique=True)
    tableau = JSONField(default=dict)
    # !!! vérifier options !!!
    dt = models.DurationField(null=True)


class Produit(models.Model):
    """
        modèle recensant les différents produits proposés à l'abonnement
    """
    # vérifier les choices et paramètres à conserver
    shortname = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=40)
    regle = models.ForeignKey(Regle, on_delete=models.PROTECT)
    entete = models.CharField(max_length=12, unique=True)
    grains = JSONField(default=dict)
    couverture = JSONField(default=dict)
    timezone = models.CharField(max_length=40)


class Cdp(models.Model):
    """ classe liant un fichier de grain:seuil pour un réseau à un produit """

    name = models.CharField(max_length=100)
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    reseau = models.DateTimeField()
    reception = models.DateTimeField()
    seuils_grains = JSONField(default=dict)
    seuils_troncons = JSONField(default=dict, null=True)
    retard = models.BooleanField(default=False)
    statut_carto = models.BooleanField(default=False)
    statut_etats = models.BooleanField(default=False)
    statut_avertissements = models.BooleanField(default=False)
    statut_diffusions = models.BooleanField(default=False)
    statut_acquitements = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['produit', 'reseau'], name='unique_reseau_par_produit')
        ]

    @classmethod
    def create(cls, cdp_file):
        """
            retourne un object cdp à partir d'un fichier uploadé
            attention : renvoie None pour les problèmes courants
        """
        cdp = Cdp()
        logger.debug(type(cdp_file.file))
        cdp.brut = cdp_file.read()
        cdp.name = cdp_file.name
        # TODO regex en paramètres !!!
        try:
            cdp.produit = Produit.objects.get(
                shortname=ENTETES_PRODUITS[cdp.name[:11]])
        except:
            logger.warning(f'{cdp.name} ne correspond pas à un produit connu')
            return None
        data = [l.decode('utf-8').split(';') for l in cdp.brut.splitlines()]
        # cdp.nom_produit = ENTETES_PRODUITS[cdp.name[:11]]
        header = data[0]
        logger.debug(re.search('.(\d{12})', cdp.name).group(1))
        # TODO add more checks on cdp
        reg_reseau = re.search('(\d{6}).(\d{6})', cdp.name)
        reseau = reg_reseau.group(2)+reg_reseau.group(1)
        logger.debug(header[0])
        if header[0] != reseau:
            logger.warning(f'{cdp.name} pb heure réseau')
            return None
        cdp.reseau = datetime.strptime(
            header[0], '%Y%m%d%H%M').replace(tzinfo=timezone.utc)
        # TODO modif ce == 'V' qui fait mal aux yeux
        total_ligne = int(header[1])
        if cdp.produit.shortname[0] == 'V':
            total_ligne += int(header[2])
        logger.debug(f'nbr de lignes: {len(data) -1} | nbr annoncé: {total_ligne}')
        if total_ligne != len(data) - 1:
            logger.warning(f'{cdp.name} mal formé (nbr de lignes)')
            return None            
        qs_etat = etat.EtatGrainProduit.objects.filter(
                                                    produit_id=cdp.produit_id)
        list_insee = list(qs_etat.values_list('grain__insee', flat=True))
        if re.search('.LATE$', cdp.name):
            cdp.retard = True
        # en 2 étapes pour la carto (en cas de reprise d'un fichier en bdd)
        if cdp.retard:
            cdp.data = {insee:-1 for insee in list_insee}
        else:
            if cdp.produit.shortname[0] == 'V':
                cdp.seuils_troncons = {l[0]: l[1]
                                       for l in data[1:int(header[1])+1]}
                cdp.seuils_grains = {l[0]: l[1] for l in data[int(
                    header[1])+1:int(header[2])+int(header[1])+1]}
            else:
                cdp.seuils_grains = {l[0]: l[3]
                                     for l in data[1:int(header[1])+1]}
        for dif in [x for x in set(cdp.seuils_grains.keys()) if x not in set(list_insee)]:
            logger.warning(
f'{cdp.name} contient code {dif} inconnu (seuil: {cdp.seuils_grains[dif]})')
            # ATTENTION le code insee doit être retiré du dico dans le warning
        logger.info(f'{cdp.name} créé')
        # logger.debug(cdp.data)
        logger.debug(
            f'grains :{len(cdp.seuils_grains)}, tronçons:{len(cdp.seuils_troncons)}')
        return cdp