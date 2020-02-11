def invert_dict(dico):
	"""
	 inversion d'un dictionnaire 
	 {a1:[b1, b2, ...]} => {b1:[a1, a2, ...} for all key/value in dico

	"""
    for key, value in dico.items():
        for i in value:
            dicinv.setdefault(i, []).append(key)
    return dicinv