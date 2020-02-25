import threading
from mflog import get_logger
import csv

import time

# fonctions de comparaison de seuils et autre
from . import utils

class TraitementEtatGrains(threading.Thread):
    def __init__(self, cdp, **kwargs):
        self.cdp = cdp
        super().__init__(**kwargs)

    def run(self):
        logger = get_logger("apicvf_django")
        logger.debug("démarrage du traitement des états")
        data = self.cdp.readlines()
        #header = data[0].split(';')
        logger.debug(type(data))
        logger.debug(f'{self.cdp.name} {self.cdp.size} {self.cdp.content_type} {self.cdp.charset}')
        csvdata = csv.reader([line.decode('utf-8') for line in data], delimiter=';')
        
        logger.debug("états : traitement effectué")
        return True