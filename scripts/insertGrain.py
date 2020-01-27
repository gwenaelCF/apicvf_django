"""insertion des gains et départements"""
import os
import csv

from injectionCdP import models

filename = './data/communes-01012019.csv'

with open(filename,'r',encoding='utf-8-sig') as f:
    reader = csv.reader(f.readlines())
    header = next(reader)
    count = 0
    for d in reader:
        tempArgs = dict(zip(header,d))
        if tempArgs['typecom'] in ['COMD','COMA']:
            continue
        rgs = { 
                'insee' : tempArgs['com'],
                'tncc' : tempArgs['tncc'],
                'ncc' : tempArgs['ncc'],
                'nccenr' : tempArgs['nccenr'],
                'dept' : models.Dept.objects.get(insee=tempArgs['dep']),
                } 
            

        try :
            grain, created = models.Grain.objects.get_or_create(**rgs)
            print(grain.ncc + (' a été créé' if created else ' existe déjà'))
            count += 1
        except Exception as e:
            print(f'pb avec {d}')
            print(e.message)
    print(f'ok pour {count}')


