regle_apic_file = './procedere/data/tableau_regle_apic.csv'
regle_vf_file = './procedere/data/tableau_regle_vf.csv'

def get_liste_cas():
    """ renvoie le dico pour l'ensemble des cas possible """

    liste_cas = {}
    
    with open(filename,'r') as f:
        junk = f.readline()
        for l in f.readlines():
            cas = l.strip('\n').split(';')
            liste_cas[tuple(int(cas[i]) for i in [0,1,2])]=False if cas[3]=='ras' else True
    return liste_cas

def generate_set(fichier, delai=False):
    """ creation de set pour les regles à partir d'un fichier csv
        en cas de délai applicable, les use-case sont divisé 
        par clés True ("dans le délai")/ False ("pas dans le délai")
        TODO : générer à partir d'un json en base
    """
    with open(fichier, 'r') as f:
        tableau  = f.read().splitlines()
    if delai :
        dico = {}
        dico[False]=set()
        dico[True]=set()
        for l in tableau :
            cas = l.split(';')
            if cas[4] == 'True':
                if cas[0] == 'True':
                    dico[True].add(tuple(int(cas[i]) for i in range(1,4)))
                else :
                    dico[False].add(tuple(int(cas[i]) for i in [2,3]))
    else :
        dico = set()
        for l in tableau:
            cas = l.split(';')
            if cas[3] == 'True':
                dico.add(tuple(int(cas[i]) for i in range(3)))
    return dico


""" dicos générés """
# apic (t_2,t_1,t0)
# vf hors_délai:(t_1,t0), dans_délai:(derniere_alerte, t_1, t0)
dico_cas_apic = {(0, 1, 2), (1, -1, -1), (1, 0, 1), (0, -1, -1), (-1, 0, 1), (2, 0, 1), (0, 0, 2), (-1, 0, 2), (2, 0, 2), (0, 0, 1), (0, -1, 1), (-1, 1, 2), (2, 1, 2), (-1, -1, 2), (0, -1, 2), (-1, -1, 1), (1, 1, 2), (1, 0, 2), (1, -1, 2)}
dico_cas_vf = {False: {(0, 1), (1, 2), (-1, 1), (2, 2), (-1, 2), (2, 1), (1, 1), (-1, -1), (0, 2)}, True: {(-1, -1, 2), (-1, 0, 2), (-1, -1, 1), (1, -1, -1), (1, 1, 2), (-1, 0, 1), (1, 0, 2), (1, -1, 2)}}
