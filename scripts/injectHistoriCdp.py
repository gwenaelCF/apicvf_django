from django.db import IntegrityError

import cdp
import injectionCdP


def run():
    for batch in cdp.models.BatchCdp.objects.all():
        for caydaypay in cdp.models.CdpApic.objects.filter(batch=batch):
            for grain in caydaypay.grains.keys():
                histo = cdp.models.HistoriCdp()
                histo.produit = caydaypay.produit
                histo.ts = caydaypay.dt
                histo.grain = injectionCdP.models.Grain.objects.get(insee=grain)
                histo.seuil = caydaypay.grains[grain]
                try :
                    histo.save()
                except IntegrityError as e:
                    print(e.__cause__)