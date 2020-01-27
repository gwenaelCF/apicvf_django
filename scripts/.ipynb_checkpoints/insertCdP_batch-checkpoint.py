import os
import re

from cdp import models

batch1 = 'injectionCdP/cdp_batch/dir_listLinks_191203'
batch2 = 'injectionCdP/cdp_batch/dir_listLinks_191130_191201'
batch3 = 'injectionCdP/cdp_batch/dir_listLinks_191201000359'

batches = [batch1, batch2, batch3]

def createBatch(batch):
    name = re.search('(?<=listLinks_).*',batch).group()
    models.BatchCdp(name=name).save()
    cdps = (models.CdpApic.create(batch+'/'+cdp, name) for cdp in os.listdir(batch))
    models.CdpApic.objects.bulk_create(cdps)



def run():
    for b in batches:
       createBatch(b)