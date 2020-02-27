import json

from carto import traitement_carto as tc 
from django.conf import settings
from django.core.files import File
from django.test import TestCase
from procedere import models as pm

'''
Tests pour le processsus de génération des json pour la carto
Usage: 
- Le fichier CDP à tester doit être placé sous carto/data/cdp_in
- Les fichiers json (à comparer avec ceux générés) doivent être placés sous carto/data/json
''' 
class CdpTestCase(TestCase):
  
    # input cdp folder
    cdp_in_folder = '/carto/data/cdp_in/'
    # expected json folder  
    json_folder = '/carto/data/json/'
    # json destination path
    dest_path = '/var/www/static-carto/'
    
    def test_cdp_apic_nc_ok(self):
        '''
        Nominal test APIC-NC
        '''
        
        # CDP input file
        cdp_in_file_name = 'FPFR43_NWBB_250930.20200225093513_P9999PU212D_LFPWA.119.LT'
        cdp_in_file_path = settings.BASE_DIR + self.cdp_in_folder + cdp_in_file_name
        # JSON expected results
        json_result_cdp_file_name = 'apic_nc_202002250930.json'
        json_expected_result_cdp_file_path = settings.BASE_DIR + self.json_folder + json_result_cdp_file_name
        json_result_reseaux_file_name = 'apic_nc_reseaux.json'
        json_expected_result_reseaux_file_path = settings.BASE_DIR + self.json_folder + json_result_reseaux_file_name
        # JSON result
        json_result_cdp_file_path = self.dest_path + json_result_cdp_file_name
        json_result_reseaux_file_path = self.dest_path + json_result_reseaux_file_name
        
        # 1. Create Cdp object from cdp file
        with open(cdp_in_file_path, 'rb') as f:
            cdpFile = File(f)
            cdpFile.name = cdp_in_file_name
            cdp = pm.produit.Cdp.create(cdpFile)
        
        # 2. Launch process carto, check result
        carto_process = tc.TraitementCarto(cdp)
        cdp.statut_carto = carto_process.process()
        
        self.assertTrue(cdp.statut_carto)      
        
        # 3. Check JSON CDP
        with open(json_expected_result_cdp_file_path) as json_file:
            data_json_expected_result_cdp = json.load(json_file)
        with open(json_result_cdp_file_path) as json_file:
            data_json_result_cdp = json.load(json_file)
        
        self.assertEqual(data_json_expected_result_cdp, data_json_result_cdp)
        
        # 4. Check JSON reseaux
        with open(json_expected_result_reseaux_file_path) as json_file:
            data_json_expected_result_reseau = json.load(json_file)
        with open(json_result_reseaux_file_path) as json_file:
            data_json_result_reseaux = json.load(json_file)
        
        self.assertEqual(data_json_expected_result_reseau, data_json_result_reseaux)
    
    
    def test_cdp_apic_fr_ok(self):
        '''
        Nominal test APIC-FR
        '''           
