
import time

def regles_vf(derniere_alerte, t0, t_1, dt):
    """
    retourne True si une alerte de seuil t0 est diffusée

    derniere_alerte : object représentant la dernière alerte diffusée
    t0 : seuil du dernier réseau (en cours de traitement)
    t_1 : seuil de l'avant-dernier réseau (dernier traité)
    dt : paramètre de persistance des alertes (6 heures d'après la doc)
    
    """
    if  t0 in [1,2]:
        if t0>derniere_alerte.seuil or (derniere_alerte.time+dt)<time.time():
            return True
    if t0 == -1:
        if (derniere_alerte.time+dt)<time.time() and t_1 == -1:
            return True
    return False
