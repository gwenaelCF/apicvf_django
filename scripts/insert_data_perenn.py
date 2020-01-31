import csv

import apicvf

def insert_produits():
    for prod in apicvf.models.PRODUITS:
        apicvf.models.Produit.objects.get_or_create(name=prod[0])

def insert_reg(dicteur):
    liste_reg = []
    for d in dicteur:
        reg = apicvf.models.Region(insee=d['reg'])
        for l in ['cheflieu', 'tncc', 'ncc', 'nccenr', 'libelle']:
            setattr(reg,l,d[l])
        if int(reg.insee)>9:
            reg.metrop=True
        liste_reg.append(reg)
    apicvf.models.Region.objects.bulk_create(liste_reg, batch_size=1000)

def insert_dept(dicteur):
    liste_dept = []
    liste_reg = apicvf.models.Region.objects.only('id', 'insee')
    for d in dicteur:
        dept = apicvf.models.Dept(insee=d['dep'])
        for l in ['cheflieu', 'tncc', 'ncc', 'nccenr', 'libelle']:
            setattr(dept,l,d[l])
        dept.region=liste_reg.get(insee=d['reg'])
        if int(d['reg'])>9 :
            dept.metrop = True
        liste_dept.append(dept)
    apicvf.models.Dept.objects.bulk_create(liste_dept, batch_size=1000)

def insert_grain(dicteur):
    liste_grain = []
    liste_dept = apicvf.models.Dept.objects.only('id', 'insee')
    for d in dicteur:
        if d['typecom'] in ['COM', 'ARM']:
            grain = apicvf.models.Grain(insee=d['com'])
            for l in ['dep', 'arr', 'tncc', 'ncc', 'nccenr', 'libelle']:
                setattr(grain,l,d[l])
            grain.dept =  liste_dept.get(insee=d['dep'])
            if int(d['reg'])>9:
                grain.metrop = True
            liste_grain.append(grain)
    apicvf.models.Grain.objects.bulk_create(liste_grain, batch_size=1000)


def insert_etat():
    dico_etat = {'dep':[],'grain':[]}
    for produit in apicvf.models.Produit.objects.all():
        for dept in apicvf.models.Dept.objects.all():
            d = apicvf.models.Etat_dept_produit(produit=produit, dept = dept)
            dico_etat['dep'].append(d)
        for grain in apicvf.models.Grain.objects.all():
            g = apicvf.models.Etat_grain_produit(produit=produit, grain = grain)
            dico_etat['grain'].append(g)

    apicvf.models.Etat_dept_produit.objects.bulk_create(dico_etat['dep'], batch_size=1000)
    apicvf.models.Etat_grain_produit.objects.bulk_create(dico_etat['grain'], batch_size=1000)


def insert_souscript_nat():
    souscript, created = apicvf.models.Souscription.objects.get_or_create(
                        produit=apicvf.models.Produit.objects.get(name='AFR'))

def run():
    print(f'produits')
    insert_produits()


    filepath = './apicvf/data/'
    filereg = filepath+'region2019.csv'
    filedept = filepath+'departement2019.csv'
    filecom = filepath+'communes-01042019.csv'
    list_com, list_dept, list_reg = [], [], []

    print(f'regions')

    with open(filereg,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_reg(dicteur)

    print(f'dept')
    with open(filedept,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_dept(dicteur)

    print(f'grains')
    with open(filecom,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_grain(dicteur)

    print(f'etats')
    insert_etat()

    print(f'souscript_nat')
    insert_souscript_nat()

    print(f'ouf')
    
