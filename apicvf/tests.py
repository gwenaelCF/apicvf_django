from django.test import TestCase
from injectionCdP import models
# Create your tests here.

class GrainTestCase(TestCase):
    def test_can_create(self):
        grain = models.Grain(insee=55555,dep='092',metrop=True)
        self.assertEqual(grain.insee,55555)
        self.assertEqual(grain.dep,'092')
        self.assertEqual(grain.etat,{'t-2':0,'t-1':0,'t0':0})
        self.assertEqual(grain.metrop,True)

        grain.save()

        gDB = models.Grain.objects.get(insee=55555)
        print(gDB)
        self.assertEqual(gDB.dep,'092')
        self.assertEqual(gDB.etat,{'t-2':0,'t-1':0,'t0':0})
        self.assertEqual(gDB.metrop,True)

class AbonnementTestCase(TestCase):
    def test_can_create(self):
        abo = models.Abonnement()
        self.assertEqual(abo.emprise,{})
        self.assertEqual(abo.etat, {'t-2':0,'t-1':0,'t0':0})
        self.assertEqual(abo.produit,'A')

        abo.save()

        aboDb = models.Abonnement.objects.get(produit='A')
        print(aboDb)