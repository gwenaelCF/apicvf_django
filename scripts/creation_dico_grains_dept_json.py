import procedere
import json
import os

def run():
    '''
    Run script creation_dico_grains_dept_json
    '''
    path = 'scripts/output/'
    
    listdept = {}
    for dept in procedere.models.granularite.Dept.objects.only('insee'):
        listdept[dept.insee]=list(dept.grain_set.all().values_list('insee',flat=True))
    
    # add NC
    listdept['988'] = list(procedere.models.granularite.Grain.objects.filter(insee__startswith='988').values_list('insee',flat=True))
    
    # sort
    for key,value in listdept.items():
        value.sort()
    
    # generate json
    if(not os.path.isdir(path)):
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        
    file = 'grains_dept.json'
    with open(path + file, 'w') as outfile:
        json.dump(listdept, outfile, separators=(',', ':'))
        
    print(f'Fichier {path}{file} généré!')