import os

from injectionCdP import models

filename = './injectionCdP/data/depts2016.txt'

with open(filename,'r',encoding='latin-1') as f:
    f.readline()
    count = 0
    for d in f.readlines():
        data = d.rstrip('\n').split('\t')
        print(data)
        rgs = dict(zip(['region','insee','cheflieu','tncc','ncc','nccenr'],data))
        try :
            dept, created = models.Dept.objects.get_or_create(**rgs)
            print(dept.ncc + (' a été créé' if created else ' existe déjà'))
            count += 1
        except e:
            print(f'pb avec {data}')
            print(e.message)
    print(f'ok pour {count}')
