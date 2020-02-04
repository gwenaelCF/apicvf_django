from cdp.models import *

def run(cdp_incoming):
    print('in test_cdp ok')
    apicCdp = CdpApic(cdp_incoming)
    print(apicCdp.datetime, apicCdp.grains)
    print('all ok')