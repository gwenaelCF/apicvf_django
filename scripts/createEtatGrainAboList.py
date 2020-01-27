import injectionCdP

listGrain = injectionCdP.models.Grain.objects.all()
for g in listGrain:
    listAbo = g.abonnement_set.all()
    if listAbo :
        etatg = injectionCdP.models.EtatGrainProduit.objects.get(grain__id__exact=g.id)
        etatg.aboList = etatg.aboList + ';'.join((abo.id for abo in listAbo))+';'
        etatg.save()
