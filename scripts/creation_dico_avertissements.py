regle_apic_file = './apicvf/data/tableau_regle_apic.csv'
regle_vf_file = './apicvf/data/tableau_regle_vf.csv'

def get_liste_cas():
    """ renvoie le dico pour l'ensemble des cas possible """

    liste_cas = {}
    
    with open(filename,'r') as f:
        junk = f.readline()
        for l in f.readlines():
            cas = l.strip('\n').split(',')
            liste_cas[tuple(int(cas[i]) for i in [0,1,2])]=False if cas[3]=='ras' else True
    return liste_cas
 
""" dicos généré précédemment """
dico_cas_apic ={(-1, -1, -1): False, (-1, -1, 0): False, (-1, -1, 1): True, (-1, -1, 2): True, (-1, 0, -1): False, (-1, 0, 0): False, (-1, 0, 1): True, (-1, 0, 2): True, (-1, 1, -1): False, (-1, 1, 0): False, (-1, 1, 1): False, (-1, 1, 2): True, (-1, 2, -1): False, (-1, 2, 0): False, (-1, 2, 1): False, (-1, 2, 2): False, (0, -1, -1): True, (0, -1, 0): False, (0, -1, 1): True, (0, -1, 2): True, (0, 0, -1): False, (0, 0, 0): False, (0, 0, 1): True, (0, 0, 2): True, (0, 1, -1): False, (0, 1, 0): False, (0, 1, 1): False, (0, 1, 2): True, (0, 2, -1): False, (0, 2, 0): False, (0, 2, 1): False, (0, 2, 2): False, (1, -1, -1): True, (1, -1, 0): False, (1, -1, 1): False, (1, -1, 2): True, (1, 0, -1): False, (1, 0, 0): False, (1, 0, 1): True, (1, 0, 2): True, (1, 1, -1): False, (1, 1, 0): False, (1, 1, 1): False, (1, 1, 2): True, (1, 2, -1): False, (1, 2, 0): False, (1, 2, 1): False, (1, 2, 2): False, (2, -1, -1): False, (2, -1, 0): False, (2, -1, 1): False, (2, -1, 2): False, (2, 0, -1): False, (2, 0, 0): False, (2, 0, 1): True, (2, 0, 2): True, (2, 1, -1): False, (2, 1, 0): False, (2, 1, 1): False, (2, 1, 2): True, (2, 2, -1): False, (2, 2, 0): False, (2, 2, 1): False, (2, 2, 2): False}
dico_cas_vf ={(0, -1, -1): True, (1, -1, -1): True, (-1, -1, -1): False, (2, -1, -1): False, (-1, 0, -1): False, (0, 0, -1): False, (1, 0, -1): False, (2, 0, -1): False, (-1, 1, -1): False, (0, 1, -1): False, (1, 1, -1): False, (2, 1, -1): False, (-1, 2, -1): False, (0, 2, -1): False, (1, 2, -1): False, (2, 2, -1): False, (-1, -1, 0): False, (0, -1, 0): False, (1, -1, 0): False, (2, -1, 0): False, (-1, 0, 0): False, (0, 0, 0): False, (1, 0, 0): False, (2, 0, 0): False, (-1, 1, 0): False, (0, 1, 0): False, (1, 1, 0): False, (2, 1, 0): False, (-1, 2, 0): False, (0, 2, 0): False, (1, 2, 0): False, (2, 2, 0): False, (-1, -1, 1): True, (0, -1, 1): True, (1, -1, 1): False, (2, -1, 1): False, (-1, 0, 1): True, (0, 0, 1): True, (1, 0, 1): True, (2, 0, 1): True, (-1, 1, 1): False, (0, 1, 1): False, (1, 1, 1): False, (2, 1, 1): False, (-1, 2, 1): False, (0, 2, 1): False, (1, 2, 1): False, (2, 2, 1): False, (-1, -1, 2): True, (0, -1, 2): True, (1, -1, 2): True, (2, -1, 2): False, (-1, 0, 2): True, (0, 0, 2): True, (1, 0, 2): True, (2, 0, 2): True, (-1, 1, 2): True, (0, 1, 2): True, (1, 1, 2): True, (2, 1, 2): True, (-1, 2, 2): False, (0, 2, 2): False, (1, 2, 2): False, (2, 2, 2): False}
