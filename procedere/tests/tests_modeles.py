from django.test import TestCase
from django.db import IntegrityError, transaction

from procedere.models.granularite import Region, Dept, Grain

# Create your tests here.


class GranularityTestCase(TestCase):
    """ Teste le modèle de granularité """
    # def setUp(self):
    #    pass

    def test_granularite(self):
        # Aucun grain initialement
        r = len(list(Region.objects.all()))
        self.assertEqual(r, 0)

        # Saisie d'une région
        code_insee = '1122'
        reg = Region(cheflieu='Toulon', insee=code_insee, tncc=1,
                     ncc='sdf', nccenr='df ', libelle='PACA', metrop=True)
        reg.save()

        # Teste le modèle de région
        # ------------------------------------------------

        # Teste si la région a été insérée
        r = len(list(Region.objects.all()))
        self.assertEqual(r, 1)

        # le libellé ne peut pas être vide
        with self.assertRaises(IntegrityError, msg="Le libellé ne devrait pas être vide."):
            with transaction.atomic():
                Region.objects.create(insee='11', libelle='')

        # le code insee doit être unique
        with self.assertRaises(IntegrityError, msg="Le code insee ne peut pas être en double."):
            with transaction.atomic():
                Region.objects.create(insee=code_insee, libelle='ret')

        # Teste le modèle Dept
        # ------------------------------------------------
        # Crée un département
        dep = Dept(region=reg, cheflieu='Nice', insee='06', tncc=1,
                   ncc='sdf', nccenr='df ', libelle='PACA', metrop=True)
        dep.save()

        d = len(list(Dept.objects.all()))
        self.assertEqual(d, 1)  # Test si le département a été inséré

        # le libellé ne peut pas être vide
        with self.assertRaises(IntegrityError, msg="Le libellé ne devrait pas être vide."):
            with transaction.atomic():
                Dept.objects.create(insee='11', libelle='')

        # Teste le modèle Grain
        # ------------------------------------------------
        gr = Grain(dept=dep, arr='Nice', cp='06200', insee='06051',
                   tncc=1, ncc='sdf', nccenr='df ', libelle='PACA', metrop=True)
        gr.save()

        gr = len(list(Grain.objects.all()))
        self.assertEqual(gr, 1)  # Test si le grain a été inséré


class ProduitTestCase(TestCase):
    """ Teste le modèle Produit """
    # def setUp(self):
    #    pass

    def test_produit(self):
        pass


class EtatTestCase(TestCase):
    """ Teste le modèle Etat """
    # def setUp(self):
    #    pass

    def test_etat(self):
        pass
