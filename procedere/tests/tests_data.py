from django.test import TestCase
from django.db import IntegrityError, transaction

from procedere.models.granularite import Region, Dept, Grain

from django.core.management import call_command





class InsertDataPerennTestCase(TestCase):
    """ Teste le modèle de granularité """
    #def setUp(self):
    #    pass

    def test_insertGrain(self):
        call_command('insert_data_perenn', 'grains', '-d', 'tests/jeux_tests_data/jeux1') #, stdout=out)
        #self.assertIn('Expected output', out.getvalue())