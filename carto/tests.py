import json
import os

from parameters import models as param
from carto import traitement_carto as tc 
from django.conf import settings
from django.core import management
from django.core.files import File
from django.test import TestCase
from procedere import models as pm
from mflog import get_logger
from helpers import *

'''
Tests pour le processsus de génération des json pour la carto
Usage: 
- 1. Le fichier CDP à tester doit être placé sous carto/data/cdp_in
- 2. Les fichiers json (à comparer avec ceux générés) doivent être placés sous carto/data/json
- 3. Le fichier testing_data.json doit être mis à jour pour associer le fichier cdp avec les fichiers json résultats
Note: Les CDPs sont traités dans l'ordre du fichier testing_data.json
''' 
class CdpTestCase(TestCase):
  
    # testing data file
    testing_data_file = '/carto/data/testing_data.json'
    # input cdp folder
    cdp_in_folder = '/carto/data/cdp_in/'
    # expected json folder  
    json_folder = '/carto/data/json/'
    
    @classmethod
    def setUpTestData(cls):
        '''
        Set up data for the whole TestCase
        '''
        with timing.Timer() as t:
            management.call_command('insert_data_perenn', 'tout', verbosity=0)

        print(f'Base mise en place en {t.interval}')

    def setUp(self):
        '''
        Default setUp
        '''
        self.logger = get_logger("apicvf_django.carto.tests")
        # update json destination path for tests
        param.set_value('app', 'chemin_carto', param.get_value('app', 'chemin_carto') + 'tests/')
        # get json destination path
        self.dest_path = param.get_value('app', 'chemin_carto')


    def test_cdp_main(self):
        '''
        Nominal tests
        '''
        self.logger.info(f'Début des tests')

        with open(settings.BASE_DIR + self.testing_data_file) as json_file:
            data_json = json.load(json_file)
            for cdp, results in data_json.items():
                # subTest permet d'exécuter l'intégralité des tests
                with self.subTest(cdp=cdp,results=results):
                    self.logger.info(f'Lancement du test pour le fichier {cdp}')
                    self.launch_cdp(cdp,results['cdp'],results['reseaux'])  

        self.logger.info(f'Fin des tests')        
    
    def launch_cdp(self, cdp, json_result_cdp, json_result_reseau):
        '''
        Lancement du test pour un fichier CDP
        :param cdp: cdp file
        :param json_result_cdp: result cdp json file
        :param json_result_reseau: result cdp reseaux file
        '''
        # CDP input file
        cdp_in_file_path = settings.BASE_DIR + self.cdp_in_folder + cdp
        # JSON expected results
        json_expected_result_cdp_file_path = settings.BASE_DIR + self.json_folder + json_result_cdp
        json_expected_result_reseaux_file_path = settings.BASE_DIR + self.json_folder + json_result_reseau
        # JSON real result
        json_result_cdp_file_path = self.dest_path + json_result_cdp
        json_result_reseaux_file_path = self.dest_path + json_result_reseau
        
        # 1. Create Cdp object from cdp file
        cdp = self.createCdpObjectFromFile(cdp_in_file_path)
        
        # 2. Launch process carto
        status = self.launchCartoProcess(cdp)

        # A. Check result
        self.assertTrue(status)  
     
        # B. Check JSON CDP
        json_cdp = self.load_json(json_expected_result_cdp_file_path, json_result_cdp_file_path)
        self.assertEqual(json_cdp[0], json_cdp[1])
        
        # C. Check JSON reseaux
        json_reseaux = self.load_json(json_expected_result_reseaux_file_path, json_result_reseaux_file_path)       
        self.assertEqual(json_reseaux[0], json_reseaux[1])

    def load_json(self, file1, file2):
        '''
        Chargement des fichiers json à comparer
        :param file1: chemin du premier fichier json
        :param file2: chemin second fichier json
        :return: Une liste avec les deux json à comparer
        '''
        with open(file1) as json_file:
            data_json_file1 = json.load(json_file)
        with open(file2) as json_file:
            data_json_file2 = json.load(json_file)   
        return [data_json_file1, data_json_file2]

    def launchCartoProcess(self, cdp):
        '''
        Lancement du processus carto
        :param cdp: Objet Cdp
        :return: True en cas de succès, False sinon
        '''
        carto_process = tc.TraitementCarto(cdp)
        return carto_process.process()

    def createCdpObjectFromFile(self, cdp_in_file_path):
        '''
        Instantiation de l'objet Cdp à parti du fichier
        :param cdp_in_file_path: Chemin du fichier Cdp
        :return: L'objet Cdp
        '''
        with open(cdp_in_file_path, 'rb') as f:
            cdpFile = File(f)
            cdpFile.name = os.path.basename(cdp_in_file_path)
            cdp = pm.produit.Cdp.create(cdpFile)
        return cdp