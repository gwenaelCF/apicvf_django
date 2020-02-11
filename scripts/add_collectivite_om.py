from helpers.regex_db import  get_collectivite_outre_mer

path = 'procedere/data/'
#orig = 'communes_all.csv'
data = 'collectivite_outre_mer.txt'
dest= 'communes_all.csv'

dico_collo = get_collectivite_outre_mer(path+data)

with open(path+dest,'a') as f:
    for k,v in dico_collo.items():
        f.write('COM,"'+k+'","","",,"",'+v.upper()+(','+v)*2+',"",'+'\n')