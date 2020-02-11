import re

def get_collectivite_outre_mer(fichier):
    with open(fichier, 'r') as f:
        texte = f.read()
    
    regex = re.compile('([\d ]+)([\D]+)')
    liste = regex.findall(texte)
    dico_collo = {insee.replace(' ',''):name.replace('\t','').replace('\n','') 
                    for (insee,name) in liste}
    return dico_collo