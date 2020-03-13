""" module permettant de générer les tableaux de régle
    pour les produits connus à ce jour (ie APICv2 et VFv2)

    tableau de la forme
    DA : seuil de dernière alerte (0 si hors délai)
    t_2, t_1, t0 : trois derniers seuils de l'objet
    pour toute combinaison (DA,t_2,t_1,t0)=> True si alerte de niveau t0
"""


class Combination:
    def __init__(self, DA, t_2, t_1, t0):
        self.DA = DA
        self.t_2 = t_2
        self.t_1 = t_1
        self.t0 = t0
        self.tupl = (self.DA, self.t_2, self.t_1, self.t0)


class TableauDeRegle:
    seuils = range(-1, 3)

    @classmethod
    def iter_possible(cls):
        return [(DA, t_2, t_1, t0) for DA in cls.seuils
                    for t_2 in cls.seuils for t_1 in cls.seuils
                    for t0 in cls.seuils
                ]

    @classmethod
    def regl_vf_seuils(cls, derniere_alerte, heure_reseau, t0, t_1, dt):
        """
        retourne True si une alerte de seuil t0 est diffusée

        derniere_alerte : object représentant la dernière alerte diffusée
        heure_reseau : heure du dernier reseau
        t0 : seuil du dernier réseau (en cours de traitement)
        t_1 : seuil de l'avant-dernier réseau (dernier traité)
        dt : paramètre de persistance des alertes (6 heures d'après la doc)

        """
        caduc = (derniere_alerte.time + dt) <= heure_reseau
        if t0 in [1, 2]:
            if t0 > derniere_alerte.seuil or caduc:
                return True
        if t0 == -1:
            if caduc and t_1 == -1:
                return True
        return False

    @classmethod
    def regl_apic_seuils(cls, t_2, t_1, t0):
        """ règle de diffusion pour les apic """
        if t0:
            if t0 == -1:
                if (t_1 == -1 and t_2 in [0, 1]):
                    return True
            if t_1 < t0:
                return True
        return False

    @classmethod
    def regl_apic_obj(cls, obj):
        """ règle de diffusion pour les apic """
        t0 = obj.t0
        t_1 = obj.t_1
        t_2 = obj.t_2
        return cls.regl_apic_seuils(t_2, t_1, t0)

    @classmethod
    def create_tableau_vf(cls):
        """
        retourne True si une alerte de seuil t0 est diffusée

        derniere_alerte : object représentant la dernière alerte diffusée
        heure_reseau : heure du dernier reseau
        t0 : seuil du dernier réseau (en cours de traitement)
        t_1 : seuil de l'avant-dernier réseau (dernier traité)
        dt : paramètre de persistance des alertes (6 heures d'après la doc)

        """
        def short_algo(DA, t_2, t_1, t0):
            if t0 in [1, 2]:
                if t0 > DA:
                    return True
            if t0 == -1:
                if t_1 == -1 and DA in [0, 1]:
                    return True
            return False

        dico_alertes = {}
        for comb in cls.iter_possible():
            dico_alertes[comb] = short_algo(*(comb))
        return dico_alertes

    @classmethod
    def create_tableau_apic(cls):
        """
        retourne True si une alerte de seuil t0 est diffusée

        derniere_alerte : object représentant la dernière alerte diffusée
        heure_reseau : heure du dernier reseau
        t0 : seuil du dernier réseau (en cours de traitement)
        t_1 : seuil de l'avant-dernier réseau (dernier traité)
        dt : paramètre de persistance des alertes (6 heures d'après la doc)

        """
        def short_algo(DA, t_2, t_1, t0):
            return cls.regl_apic_seuils(t_2, t_1, t0)

        dico_alertes = {}
        for comb in cls.iter_possible():
            dico_alertes[comb] = short_algo(*(comb))
        return dico_alertes
