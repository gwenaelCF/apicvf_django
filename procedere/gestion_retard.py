from datetime import datetime, timedelta, timezone
import io

from django.core.files.uploadedfile import InMemoryUploadedFile
from mflog import get_logger

from procedere.models import produit, granularite, etat
from procedere.utils import GestionCdp, create_cdp
from procedere.reception_cdp import reception_cdp
from parameters import models as param

logger = get_logger('gestion_retard')

# def create_cdp_late(prod, reseau):

#     reception = (reseau+timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')
#     reseau = reseau.strftime('%Y%m%d%H%M')
#     name = prod.entete + '_' +  reseau[6:] + '.' + reception + '_XXXXXXXXXXX_XXXXX.XXX.LT.LATE'
#     # fais ça im= InMemoryUploadedFile(io.BytesIO(file),None,'unsuperfichier','_io.BytesIO',file.__sizeof__(),'UTF-8')
#     liste_insee = granularite.Grain.objects.filter(
#                             id__in=prod.etatgrainproduit_set.values_list('grain_id', flat=True)
#                             ).values_list('insee', flat=True)

#     #TODO revoir le format en fonction des choix definitifs pour les CDP
#     texte = bytes(reseau+';'+str(len(liste_insee)), 'UTF-8')
#     forma = ';' if prod.shortname.startswith('V') else ';;;'
#     for i in liste_insee:
#         texte += bytes(i+forma+'-1\n','UTF-8')
#     brut = io.BytesIO(texte)
#     return InMemoryUploadedFile(brut,
#                                 None,name,
#                                 '_io.BytesIO',brut.__sizeof__(),
#                                 'UTF-8')


def check_retard():
    logger.info('début de la gestion des retards')
    #chemin = param.get_value('app', 'chemin_cdp')
    dnow = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    reseau = dnow - timedelta(minutes=15) - timedelta(minutes=dnow.minute % 15)
    logger.debug(produit.Produit.objects.all())
    for prod in produit.Produit.objects.all():
        logger.info(f'{prod.name} in process')
        cdp = produit.Cdp(produit=prod)
        gestion = GestionCdp(cdp)
        if not gestion.path.joinpath(reseau.strftime('%Y%m%d%H%M')).exists():
            logger.info(
                f'{str(reseau)} de {prod.name} absent - traité en retard')
            cdp_late = create_cdp(prod, reseau)
            reception_cdp(cdp_late)
        else:
            logger.info(f'{str(reseau)} de {prod.name} trouvé, rien à faire')
