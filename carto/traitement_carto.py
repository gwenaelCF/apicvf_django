"""
Traitement CARTO
"""
from parameters import models as param
from procedere import utils, models
from datetime import datetime, timedelta
from mflog import get_logger
import os.path
import locale
import pytz
import json
import re
import os
class TraitementCarto():
    """
    Génération/Mise à jour des fichiers json pour la carto
    """
    def __init__(self, cdp, **kwargs):
        """
        Initialisation
        :param cdp: objet Cdp
        """
        # logger
        self.logger = get_logger("carto")
        # cdp object input file
        self.cdp = cdp
        # dictionaries
        self.list_dept_seuil = {}
        self.grain_dept_dict = {}
        # load parameters
        self.dest_path = param.get_value('app', 'chemin_carto')
        self.delta_t = int(param.get_value('app', 'carto_delta_t'))
        self.cdp_regex = param.get_value('app', 'regex_cdp')
        # locale (date in french)
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

    def process(self):
        """
        Conversion du fichier CDP en fichiers json pour la cartographie sur le front
        :return: True, si le processus réussi, False, si le projet échoue
        """
        
        try:

            self.logger.info('Début carto !')
        
            # Get the original CDP file name
            original_cdp_filename = self.cdp.name
            self.logger.info('Nom fichier : ' + original_cdp_filename)
            
            # Check file name
            if not re.match(self.cdp_regex, original_cdp_filename):
                raise NameError('Nom de fichier CDP invalide!') 
                      
            # Load grains/depts from database
            for gr_dept in models.granularite.Grain.objects.all().values('insee', 'dept__insee'):
                gr_insee = gr_dept.get('insee')
                dept_insee = gr_dept.get('dept__insee')
                # FIXME : warning! added missing '0'
                grain_6d = str(gr_insee) + '0'
                self.grain_dept_dict[grain_6d] = dept_insee

            # Extract prefix/reseau from cdp file
            cdp_prefix = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(1)
            cdp_reseau_hhmm = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(3)
            cdp_reseau_yyyymmdd = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(4)
            self.logger.info('Prefixe CDP : ' + cdp_prefix) 

            # Load product from database
            for p in models.produit.Produit.objects.filter(entete=cdp_prefix):
                p_name = p.name.split()[0].lower() # apic/vf
                p_origin = p.shortname[1:3].lower() # fr,oi,ag,nc
                product_for_file = Produit(p_name, p_origin, p.entete, p.timezone)
             
            # Date/Time 
            cdp_time_reseau = cdp_reseau_yyyymmdd + cdp_reseau_hhmm
            cdp_time_reseau_str = self.compute_date_fr(cdp_time_reseau, product_for_file.timezone)
            self.logger.info('Reseau : ' + cdp_time_reseau + ' (' + cdp_time_reseau_str + ')')
            product_for_file.timestamp = cdp_time_reseau
            product_for_file.timestamp_str = cdp_time_reseau_str
              
            # A. Process CDP
            self.logger.info("A. Processus CDP...")
            cdp_status = self.process_cdp(product_for_file)
            if not cdp_status:
                return False
            
            # B. Process list reseaux
            self.logger.info("B. Processus Reseaux...")
            reseau_status = self.process_reseaux(product_for_file)
            if not reseau_status:
                return False
        
            self.logger.info('Fin carto !')

        except Exception as e:
            # Handle exceptions
            self.logger.error(e, exc_info=True)
            return False
        
        return True

    def process_cdp(self, product_for_file):
        """
        Conversion du fichier CDP (pour ce réseau) en fichier json
        :param product_for_file: objet Produit
        :return: True, si le processus réussi, False, si le projet échoue
        """
        # json init
        data_json = {}
        data_json['communes'] = []
        data_json['troncons'] = []
        data_json['deps'] = []
        
        try:
            # Define output json file name
            provider = product_for_file.name
            self.logger.info('Fournisseur : ' + provider)
            origin = product_for_file.origin 
            self.logger.info('Origin : ' + origin)
            output_filename = provider + '_' + origin + '_' + product_for_file.timestamp + '.json'
            self.logger.info('Nom de fichier en sortie : ' + output_filename)
            
            # Read CDP
            self.logger.info('Lecture du CDP...')
            
            # In case of cdp LATE, data is given in cdp.data
            if(self.cdp.retard == True):
                grains_items = self.cdp.data.items()
            else:
                grains_items = self.cdp.seuils_grains.items()

            # Treat data
            for grain, seuil_gr in grains_items:
                try:
                    seuil = int(seuil_gr)
                    self.handle_csv_row('grain', grain, seuil, product_for_file, data_json)
                except ValueError:
                    self.logger.warning('Donnée non traitée: "' + grain + ';'+seuil_gr+'"')
                
            for troncon, seuil_tr in self.cdp.seuils_troncons.items():
                try:
                    seuil = int(seuil_tr)
                    self.handle_csv_row('troncon', troncon, seuil, product_for_file, data_json)
                except ValueError:
                    self.logger.warning('Donnée non traitée: "' + grain + ';'+seuil_tr+'"')

            # Compute threshold per department (min 0<-1<1<2 max)
            for dept, seuils in self.list_dept_seuil.items():
                seuil_max = utils.findmax(seuils)
                data_json['deps'].append({'id':dept, 'c:':str(seuil_max)}) 
            
            # Append date to json
            data_json['date'] = product_for_file.timestamp
            data_json['date_str'] = product_for_file.timestamp_str
            
            # Write output
            file_path = self.dest_path + output_filename
            with open(file_path, 'w') as outfile:
                json.dump(data_json, outfile, separators=(',', ':'), ensure_ascii=False)
            self.logger.info('Fichier généré : ' + file_path)
        
        except Exception as e:
            # Handle exceptions
            raise Exception(str(e))
            return False
        
        return True

    def process_reseaux(self, produit):
        """
        Création/mise à jour du fichier de réseau json pour ce produit
        :param prod: objet Produit
        :return: True, si le processus réussi, False, si le projet échoue
        """
        # json init
        data_json = {}
        data_json['reseaux'] = []
        i = j = 0
        
        try:
            # Define output json file name
            output_filename = produit.name + '_' + produit.origin + '_reseaux.json'
            self.logger.info('Fichier reseau : ' + output_filename)
            file_path = self.dest_path + output_filename
            
            # If file exist, load it
            if os.path.isfile(file_path):
                self.logger.info('Le fichier réseau existe')
                with open(file_path) as json_file:
                    data_json = json.load(json_file)
            
            self.logger.info('Nombre de réseaux présents : ' + str(len(data_json['reseaux'])))

            # Check if reseau already exist (once or several), if yes delete           
            while i < len(data_json['reseaux']):
                if(data_json['reseaux'][i]['date'] == produit.timestamp):
                    data_json['reseaux'].remove(data_json['reseaux'][i])
                    self.logger.warning('Le réseau existe déjà! il est supprimé')
                else:
                    i += 1
            
            # Insert reseau (top of list)
            content = {'date':produit.timestamp, 'date_str':produit.timestamp_str, 'origin':produit.origin, 'n_c':str(produit.nb_gr_nc), 'n_1':str(produit.nb_gr_1), 'n_2':str(produit.nb_gr_2)}           
            data_json['reseaux'].insert(0, content) 
            
            # Sort per date [robustness, should not happen]           
            data_json['reseaux'] = sorted(data_json['reseaux'], key=lambda k: k['date'], reverse=True)
            
            # Get the most recent reseau [robustness, should not happen]
            last_reseau = produit.timestamp
            for reseau in data_json['reseaux']:
                if reseau['date'] > last_reseau:
                    last_reseau = reseau['date']
            self.logger.info('Réseau le plus récent : ' + last_reseau)
            
            # Delete reseau older than 72h (compared to the most recent)
            datereseau_utc = datetime.strptime(last_reseau, '%Y%m%d%H%M') 
            datereseau_utc_delta_t = datereseau_utc - timedelta(hours=self.delta_t) 
            timestamp_delta_t = datereseau_utc_delta_t.strftime('%Y%m%d%H%M')
            self.logger.info('Réseaux conservés jusqu\'à : ' + timestamp_delta_t + ' (' + str(self.delta_t) + 'H)')
            
            while j < len(data_json['reseaux']):
                if(data_json['reseaux'][j]['date'] < timestamp_delta_t):
                    r_date = data_json['reseaux'][j]['date']
                    self.logger.info('Le réseau de date ' + r_date + ' est supprimé!')
                    data_json['reseaux'].remove(data_json['reseaux'][j])
                    # delete file
                    self.delete_file(produit, r_date)
                else:
                    j += 1
         
            # Write output
            with open(file_path, 'w') as outfile:
                json.dump(data_json, outfile, separators=(',', ':'), ensure_ascii=False)
            self.logger.info('Fichier réseau mis à jour !')
            
        except Exception as e:
            # Handle exceptions
            raise Exception(str(e))
            return False
        
        return True

    def handle_csv_row(self, type, elt, seuil, product_for_file, data_json):
        """
        Traite les lignes du fichier csv
        :param type: grain/troncon
        :param elt: id grain ou troncon
        :param seuil: seuil grain/troncon (int)
        :param product_for_file: l'objet produit concerné
        :param data_json: json de sortie
        """
        # troncon
        if type == 'troncon':
            data_json['troncons'].append({'id':str(elt), 'c:':str(seuil)})                      
        # grain
        elif type == 'grain':
            data_json['communes'].append({'id':str(elt), 'c:':str(seuil)})
            self.compute_dept_list(elt, seuil)
            product_for_file.add_grain(seuil)

    @classmethod        
    def compute_date_fr(self, cdp_time_reseau, timezone):
        """
        Génération de la date au format 'Mercredi 05 Février à 17:30 Loc' en fonction de la timezone (UTC+x)
        :param datetime: yyyymmddhhmm
        :param timezone: 'Europe/Paris'...
        :return: date au format attendu
        """
        datereseau_utc = datetime.strptime(cdp_time_reseau, '%Y%m%d%H%M')
        local_tz = pytz.timezone(timezone)
        local_dt = datereseau_utc.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_dt.strftime('%A %d %B à %H:%M Loc')

    def compute_dept_list(self, grain, seuil):
        """
        Génération de la liste des seuils (distincts) par département. ex: {"01":[-1,1],"02":[1,2]...}
        :param grain: (ex: 010010)
        :param seuil: (ex: 2)
        :return:
        """
        # Récupère le département correespondant au grain
        dept = self.grain_dept_dict.get(grain)
        
        # FIXME try adding a '0'
        if dept is None:
            dept = self.grain_dept_dict.get(grain + '0')
        
        if dept is None:
            self.logger.warning('Grain inconnu: ' + grain)
        else:
            try:
                self.list_dept_seuil[dept].add(seuil)
            except KeyError:
                self.list_dept_seuil[dept] = {seuil}

    def delete_file(self, produit, r_date):
        """ 
        Suppression d'un fichier json réseau
        :param produit: l'objet produit concerné
        :param r_date: le réseau concerné
        :return: 
        """
        filename = produit.name + '_' + produit.origin + '_' + r_date + '.json'
        try:
            if(os.path.exists(self.dest_path + filename)):
                os.remove(self.dest_path + filename)
                self.logger.info('Le fichier ' + filename + ' est supprimé!')
            else:
                self.logger.warning('Le fichier ' + filename + ' n\'existe pas!')
        except OSError:
            self.logger.warning('Impossible de supprimer le fichier ' + filename + '!')    
    
class Produit():
    """ 
    Objet Produit (CDP) manipulé dans le traitement carto
    """
    nb_gr_1 = 0
    nb_gr_2 = 0
    nb_gr_nc = 0
    timestamp = ''
    timestamp_str = ''

    def __init__(self, name, origin, prefix, timezone):
        self.name = name
        self.origin = origin
        self.prefix = prefix
        self.timezone = timezone
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def add_grain(self, seuil):
        seuil = int(seuil)
        if seuil == -1:
            self.nb_gr_nc += 1
        elif seuil == 1:  
            self.nb_gr_1 += 1
        elif seuil == 2:
            self.nb_gr_2 += 1  
