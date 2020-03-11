regle_apic_file = './procedere/data/tableau_regle_apic.csv'
regle_vf_file = './procedere/data/tableau_regle_vf.csv'

def get_liste_cas(filename, regle='apic'):
    """ renvoie le dico pour l'ensemble des cas possible """

    liste_cas = {}
    
    with open(filename,'r') as f:
        junk = f.readline()
        if regle == 'apic':
            for l in f.readlines():
                cas = l.strip('\n').split(';')
                liste_cas[tuple(int(cas[i]) for i in [0,1,2])]= (cas[3]=='True')
        elif regle == 'vf':
            for l in f.readlines():
                cas = l.strip('\n').split(';')
                if cas[0] == 'False':
                    cas[1] = 0
                liste_cas[tuple(int(cas[i]) for i in [1,2,3])]= (cas[4]=='True')

    return liste_cas

def generate_set(fichier, delai=False):
    """ creation de listes pour les regles à partir d'un fichier csv
        en cas de délai applicable, les use-case sont divisé 
        par clés True ("dans le délai")/ False ("pas dans le délai")
        TODO : générer à partir d'un json en base
    """
    with open(fichier, 'r') as f:
        tableau  = f.read().splitlines()
    if delai :
        dico = {False:[],True:[]}
        
        for l in tableau :
            cas = l.split(';')
            if cas[4] == 'True':
                if cas[0] == 'True':
                    dico[True].append(tuple(int(cas[i]) for i in range(1,4)))
                else :
                    dico[False].append(tuple(int(cas[i]) for i in [2,3]))
    else :
        dico = []
        for l in tableau:
            cas = l.split(';')
            if cas[3] == 'True':
                dico.append(tuple(int(cas[i]) for i in range(3)))
    return dico


""" dicos générés """
# apic (t_2,t_1,t0)
# vf hors_délai:(t_1,t0), dans_délai:(derniere_alerte, t_1, t0)
dico_cas_apic = [(-1, -1, 1), (-1, -1, 2), (-1, 0, 1), (-1, 0, 2), (-1, 1, 2), (0, -1, -1), (0, -1, 1), (0, -1, 2), (0, 0, 1), (0, 0, 2), (0, 1, 2), (1, -1, -1), (1, -1, 2), (1, 0, 1), (1, 0, 2), (1, 1, 2), (2, 0, 1), (2, 0, 2), (2, 1, 2)]
dico_cas_vf = {False: [(0, 1), (0, 2), (-1, -1), (-1, 1), (-1, 2), (1, 1), (1, 2), (2, 1), (2, 2)], True: [(-1, 0, 1), (-1, 0, 2), (-1, -1, 1), (-1, -1, 2), (1, 0, 2), (1, -1, -1), (1, -1, 2), (1, 1, 2)]}
