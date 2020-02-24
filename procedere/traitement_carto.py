import threading
from mflog import get_logger

# fonctions de comparaison de seuils et autre
from . import utils

class TraitementCarto(threading.Thread):
    def __init__(self, cdp, **kwargs):
        self.cdp = cdp
        super().__init__(**kwargs)

    def run(self):
        logger = get_logger("apicvf_django")
        logger.debug("démarrage du traitement carto")
        data = self.cdp.read()
        time.sleep(30)
        logger.debug(data)
        logger.debug("et voilà la carto")