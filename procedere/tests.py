import random
from django.test import TestCase, tag
from procedere import models, traitements, utils
from helpers import *


import scripts.insert_data_perenn





class VitesseTraitementTestCase(TestCase):
    """ uniquement pour apic pour l'instant """
    nbAbo= 400000
    grainParAbo = 400
    weights=[0, 10000, 10000, 10000]
    cycles=3

    def randomChoice(self, insee_list, weights=[9985, 9990, 9999, 10000]):
        return random.choices([0,-1,1,2], cum_weights= weights, k=insee_list)
    
    def get_random_abo(self):
        return random.choices(range(self.nbAbo),k=self.grainParAbo)

    def insert_abo(self):
        list_etat = models.etat.Etat_grain_produit.objects.filter(
            produit__name__exact='AFR').only('id')
        for etat in list_etat:
            etat.abo_array=self.get_random_abo()
        models.etat.Etat_grain_produit.objects.bulk_update(list_etat,['abo_array'],batch_size=5000)
    
    def setUp(self):
        with timing.Timer() as t:
            scripts.insert_data_perenn.run()

        print(f'base mise en place en {t.interval}')



    def create_fake_cdp(self, insee_list):
        print(f'génération cdp')
        with timing.Timer() as t:
            randList = self.randomChoice(len(insee_list), self.weights)
            fakeCdp = {insee_list[i]:randList[i] for i in range(len(insee_list))}    
        print(f'fait en {t.interval}'+
                f'pour une longueur de {len(fakeCdp.keys())}')
        return fakeCdp

    def applatissement(self, fakeCdp):
        print(f'début applatissement')
        etat_qs = models.etat.Etat_grain_produit.objects.filter(
            produit__name__exact='AFR').values(
            'id','grain__insee','t_2', 't_1', 't0','abo_array')
        alertAbo = {-1:0,1:0,2:0}
        with timing.Timer() as t:
            dico_etat_abo = {etat['grain__insee']:(
                etat['abo_array'],etat['t_2'], etat['t_1'], etat['t0']) 
                                for etat in etat_qs
                            }
        print(
            f'dico des grains:[abos] fait en {t.interval}'+
            f' pour {len(dico_etat_abo.keys())} clés')
        with timing.Timer() as t:
            dico_abo_etat0 = {}
            for insee, newt0 in fakeCdp.items():
                if newt0 != 0:
                    for abo in dico_etat_abo[insee][0]:
                        dico_abo_etat0.setdefault(abo, []).append(
                            (dico_etat_abo[insee][2], dico_etat_abo[insee][3], newt0)
                            )
            for abo, etats in dico_abo_etat0.items():
                etats = [utils.findMax(seuils) for seuils in zip(*etats)]
                dico_abo_etat0[abo]=etats
                if utils.regl_apic_seuils(etats[0],etats[1],etats[2]):
                    alertAbo[etats[2]]+=1
        print(f'applatissement fait en {t.interval}')
        return dico_etat_abo, dico_abo_etat0, alertAbo

    def updateGrainDB(self, fakeCdp):
        seuils = {0:[],-1:[],1:[],2:[]}
        with timing.Timer() as t:
            print(f'création dico des seuils de grains')    
            for insee, seuil in fakeCdp.items():
                seuils[seuil].append(insee)
            print(f'update (état)grains en base')
            for key in seuils.keys():
                utils.modifSeuilBatch(
                        models.etat.Etat_grain_produit.objects.filter(
                            grain__insee__in=seuils[key]),
                        key
                )
        print(f'fait en {t.interval}')

    def test_can_treat_quickly(self):
        
        print(f'starting at : {timing.whatTimeIsIt()}')
        print(
            f'param : abo={self.nbAbo}, grainParAbo={self.grainParAbo}, proba_cumulative[0,-1,1,2]={self.weights}, cycles={self.cycles}')
        #useful var
        # grain_range = injectionCdP.models.Grain.objects.aggregate(Max('id'),Min('id'))
        # grainsQl = injectionCdP.models.Grain.objects.all()
        # nbGrains = grainsQl.count()
        insee_list = list(models.etat.Etat_grain_produit.objects.filter(
            produit__name__exact='AFR').values_list('grain__insee', flat=True))
        with timing.Timer() as t:
            self.insert_abo()
        print(f'mise en place des abos par grain en {t.interval}')
        time = 0
        for j in range(self.cycles):
            with timing.Timer() as t:
                print(f"cycle {j+1} - injection d'un cdp")
                fakeCdp = self.create_fake_cdp(insee_list)
                print(f'traitement')
                dico_etat_abo, dico_abo_etat0, alertAbo = self.applatissement(fakeCdp)
                print(f'nombre d\'abo en alerte par seuil : \n{alertAbo}')
                print(f"mise à jour base")
                self.updateGrainDB(fakeCdp)
                #updateAboDB(dico_abo_etat0)
            inter = t.interval
            time += inter
            print(f'\ndurée du cyle {j+1}: {inter}\n')

        print(f'durée totale : {time} | durée par cycle : {time/self.cycles}')
        print(f'end at : {timing.whatTimeIsIt()}')
        self.assertLess(time/self.cycles, 120)