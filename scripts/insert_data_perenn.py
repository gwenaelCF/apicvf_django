import csv
import time
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
        if int(reg.insee)<=9:
            reg.metrop=False
        liste_reg.append(reg)
    apicvf.models.Region.objects.bulk_create(liste_reg, batch_size=1000)

def insert_dept(dicteur):
    liste_dept = []
    liste_reg = apicvf.models.Region.objects.only('id', 'insee', 'metrop')
    for d in dicteur:
        dept = apicvf.models.Dept(insee=d['dep'])
        for l in ['cheflieu', 'tncc', 'ncc', 'nccenr', 'libelle']:
            setattr(dept,l,d[l])
        dept.region=liste_reg.get(insee=d['reg'])
        dept.metrop = dept.region.metrop
        liste_dept.append(dept)
    apicvf.models.Dept.objects.bulk_create(liste_dept, batch_size=1000)

def insert_grain(dicteur):
    liste_grain = []
    liste_dept = apicvf.models.Dept.objects.only('id', 'insee', 'metrop')
    for d in dicteur:
        if d['typecom'] in ['COM', 'ARM']:
            grain = apicvf.models.Grain(insee=d['com'])
            for l in ['dep', 'arr', 'tncc', 'ncc', 'nccenr', 'libelle']:
                setattr(grain,l,d[l])
            grain.dept =  liste_dept.get(insee=d['dep'])
            grain.metrop = grain.dept.metrop
            liste_grain.append(grain)
    apicvf.models.Grain.objects.bulk_create(liste_grain, batch_size=5000)


def insert_etat(dicteur):
    dico_etat = {'reg':[],'dep':[],'grain':[]}
    oridict = {}
    for d in dicteur:
        oridict.setdefault(d['origin'], []).append(d['id'])
    for produit in apicvf.models.Produit.objects.all():
        apicvf.models.Etat_produit.objects.get_or_create(produit=produit)
        insee_produit = [
            insee for orig in apicvf.models.PRODUITS_DICO[produit.name] 
                    for insee in oridict[orig]
                    ]
        grains_temp, dept_temp = [], []
        gr_qs = apicvf.models.Grain.objects.filter(
                                    insee__in=insee_produit)
        for grain in gr_qs:
            g = apicvf.models.Etat_grain_produit(
                                produit=produit, grain = grain)
            grains_temp.append(g)
        dep_qs = apicvf.models.Dept.objects.filter(
                                id__in=set(gr_qs.values_list('dept',flat=True))
                                )
        for dept in dep_qs:
            d = apicvf.models.Etat_dept_produit(produit=produit, dept = dept)
            dept_temp.append(d)
        for reg in apicvf.models.Region.objects.filter(
                                id__in=set(dep_qs.values_list('region', flat=True))): 
            r = apicvf.models.Etat_reg_produit(produit=produit, reg = reg)
            dico_etat['reg'].append(r)
        dico_etat['grain'].extend(grains_temp)
        dico_etat['dep'].extend(dept_temp)

    apicvf.models.Etat_reg_produit.objects.bulk_create(
                        dico_etat['reg'], batch_size=1000)
    apicvf.models.Etat_dept_produit.objects.bulk_create(
                        dico_etat['dep'], batch_size=1000)
    apicvf.models.Etat_grain_produit.objects.bulk_create(
                        dico_etat['grain'], batch_size=5000)



def run():
    t_start = time.time()
    print(f'produits')
    insert_produits()
    t_int1 = time.time()
    print(f'done in {t_int1-t_start}')

    filepath = './apicvf/data/'
    filereg = filepath+'region2019.csv'
    filedept = filepath+'departement2019.csv'
    filecom = filepath+'communes-01042019.csv'
    fileorigin = filepath+'apic_communes_2020.csv'
    #list_com, list_dept, list_reg = [], [], []
    print(f'création regions')
    with open(filereg,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_reg(dicteur)
    t_int2 = time.time()
    print(f'done in {t_int2-t_int1}')    
    print(f'création dept')
    with open(filedept,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_dept(dicteur)
    t_int3 = time.time()
    print(f'done in {t_int3-t_int2}')
    print(f'création grains')
    with open(filecom,'r',encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f) 
        insert_grain(dicteur)
    t_int4 = time.time()
    print(f'done in {t_int4-t_int3}')    
    print(f'création etats par produit')
    with open(fileorigin,'r', encoding='utf-8-sig') as f:
        dicteur = csv.DictReader(f, delimiter=';')
        insert_etat(dicteur)
    t_int5 = time.time()
    print(f'done in {t_int5-t_int4}')
    print(f'ouf')
    t_fin = time.time()
    print(f'total secondes {t_fin-t_start}')
    
