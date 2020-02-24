from django.test import TestCase
from django.db import IntegrityError, transaction

from procedere.models.granularite import Region

# Create your tests here.

class GranularityTestCase(TestCase):
    """ Teste le modèle de granularité """
    #def setUp(self):
    #    pass

    def _create_region(self, champs = []):
        """ champs=liste des champs dans l'ordre :
        'cheflieu', 'insee', 'tncc', 'ncc', 'nccenr', 'libelle', 'metrop' """
        region = Region()
        region.cheflieu = champs[0]
        region.insee = champs[1]
        region.tncc = champs[2]
        region.ncc = champs[3]
        region.nccenr = champs[4]
        region.libelle = champs[5]
        region.metrop = champs[6]
        region.save()

    def test_granularite(self):
        # Aucun grain initialement        
        r = len(list(Region.objects.all()))
        self.assertEqual(r, 0)

        # Saisie d'une région 
        champs = ['Toulon', '1122', 1, 'sdf', 'df ', 'PACA', True]
        self._create_region(champs)
        
        # Test si la région a été insérée
        r = len(list(Region.objects.all()))
        self.assertEqual(r, 1)

        # le libellé ne peut pas être vide
        with self.assertRaises(IntegrityError, msg="Le libellé ne devrait pas être vide."):
            with transaction.atomic(): 
                Region.objects.create(insee='11', libelle='')
        
        # le code insee doit être unique
        try:
            with transaction.atomic(): 
                Region.objects.create(insee='1122', libelle='ret')
            self.fail("Le code insee ne peut pas être en double.")
        except IntegrityError:
            pass

        
        



        


