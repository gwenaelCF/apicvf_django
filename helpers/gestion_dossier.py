from pathlib import Path
from mflog import get_logger

## voir si seulement utilisé dans cdp -> transfert app procedere
class GestionDossier:
    """ classe générique pour la gestion des fichiers locaux 
        dans un dossier précis

        NB : cette classe n'est pas une manipulation simulée mais agit
             directement via le système
            donc peut potentiellement casser l'application
            !!! instanciation = création !!!
    """

    logger = get_logger("helpers")

    def __init__(self, path):
        raise NotImplementedError("I'm too powerfull, use a subclass")
        #p = Path(path)
        #self.path = p
        #self.creer_chemin()

    def creer_chemin(self):
        self.path.mkdir(parents=True, exist_ok=True)
        return True

    def lister_fichiers(self):
        """ retourne la liste des fichiers d'un dossier sous forme de Path """
        return self.path.iterdir()

    def creer_fichier(self, nom, fichier, ecrase=False):
        """ création d'un fichier dans self.path
    
            nom : nom du fichier à créer
            fichier : data binaire à insérer
            ecrase : ignorer le fichier existant 
                            (mauvaise pratique en général, True pour update)
        """
        self.creer_chemin()
        try:
            self.path.joinpath(nom).touch(exist_ok=ecrase)
            self.path.joinpath(nom).write_bytes(fichier)
            self.logger.debug("fichier "+nom+" créé")
        except FileExistsError:
            self.logger.warning("fichier "+nom+" existe déjà")
            return False
        except Exception as e:
            self.logger.critical("le fichier "+nom+" n'a pas pu ẽtre créer\n"
                                 +str(e))
            return False
        return True

    def efface_moissa(self, nom=""):
        """ classe pour effacer 
            force le self.path sur le dossier parent pour éviter une erreur d'usage
        """
        if nom =="":
            self.logger.warning("pas de nom de fichier à effacer")
            return None
        try:
            effacera = self.path.joinpath(nom)
            if effacera.is_dir():
                effacera.rmdir()
            else :
                self.path.joinpath(nom).unlink()
            return True
        except FileNotFoundError as e:
            self.logger.error("le nom "+nom+" n'existe pas\n"+str(e))
            return False
        except Exception as e:
            self.logger.error(str(e))
            return False

    def trouve_fichier(self, pattern, recurs=False):
        """ trouve un fichier dans un dossier 
            recurs = True si recherche recursive
        """
        if recurs:
            return self.path.rglob(pattern)
        else :
            return self.path.glob(pattern)