from datetime import datetime, timedelta, timezone
import io

from django.core.files.uploadedfile import InMemoryUploadedFile

from procedere.models import produit, granularite, etat


def create_cdp_late(prod, reseau):

    reception = (reseau+timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')
    reseau = reseau.strftime('%Y%m%d%H%M')
    name = prod.entete + '_' +  reseau[6:] + '.' + reception + '_XXXXXXXXXXX_XXXXX.XXX.LT.LATE'
    # fais ça im= InMemoryUploadedFile(io.BytesIO(file),None,'unsuperfichier','_io.BytesIO',file.__sizeof__(),'UTF-8')
    liste_insee = granularite.Grain.objects.filter(
                            id__in=prod.etatgrainproduit_set.values_list('grain_id', flat=True)
                            ).values_list('insee', flat=True)
    
    #TODO revoir le format en fonction des choix definitifs pour les CDP
    texte = bytes(reseau+';'+str(len(liste_insee)), 'UTF-8')
    forma = ';' if prod.shortname.startswith('V') else ';;;'
    for i in liste_insee:
        texte += bytes(i+forma+'-1','UTF-8')
    brut = io.BytesIO(texte)
    return InMemoryUploadedFile(brut,
                                None,name,
                                '_io.BytesIO',brut.__sizeof__(),
                                'UTF-8')





