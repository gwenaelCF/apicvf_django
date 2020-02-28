from procedere import utils
from datetime import datetime, timedelta
from mflog import get_logger
import os.path
import locale
import pytz
import json
import csv
import re
import os


class TraitementCarto():
    """
    Traitement CARTO
    Génération/Mise à jour des fichiers json pour la carto
    """

    # FIXME : parameters to be put in param table
    # json destination path
    dest_path = '/var/www/static-carto/'
    # locale (date in french)
    locale.setlocale(locale.LC_TIME, '')
    # delta time reseaux
    delta_t = -72
    # fichiers de config
    config_product_file = '/home/mfdata/config/produits.json'
    config_grains_dept_file = '/home/mfdata/config/grains_dept.json'
    # regular expressions
    cdp_regex = '([A-Z]{4}\d{2}_[A-Z]{4})_(\d{2})(\d{4}).(\d{8})(\d{6})_(.*)\.(.*)\.LT$'
    vf_gr_regex = '^(.{5})(\d{1});(-?\d);(.*);(.*)$'
    vf_tr_regex = '^([^;]*);(-?\d)$'
    apic_gr_regex_1 = '^(.{5})(\d{1});(.*);(.*);(-?\d);.*$'  # grain
    apic_gr_regex_2 = '^(.{2});(-?\d);.*$'  # bilan dept
    # data position in row
    apic_pos_gr = 0
    apic_pos_seuil = 3 
    vf_pos_gr = 0
    vf_pos_seuil = 1
    # dictionary grain->dept
    grain_dept_dict = {}

    def __init__(self, cdp, **kwargs):
        """
        Initialisation
        :param cdp: objet Cdp
        """
        self.logger = get_logger("apicvf_django.carto")
        self.cdp = cdp
        # dictionary dept->[seuils]
        self.list_dept_seuil = {}
       
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
            
            # Load product configuration file
            product_dict = {}
            with open(self.config_product_file) as json_prod_file:
                data_p = json.load(json_prod_file)
                for p in data_p['produits']:
                    prod = Produit(p['name'], p['origin'], p['prefix'], p['timezone'])
                    product_dict[p['prefix']] = prod
            
            # Load grains/depts configuration file
            with open(self.config_grains_dept_file) as json_gr_file:
                data_gr = json.load(json_gr_file)
                for dept, grains in data_gr.items():
                    for grain in grains:
                        # FIXME : warning! added missing '0'
                        grain_6d = str(grain) + '0'
                        self.grain_dept_dict[grain_6d] = dept
    
            # Extract prefix/reseau from cdp file
            cdp_prefix = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(1)
            cdp_reseau_hhmm = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(3)
            cdp_reseau_yyyymmdd = re.search(self.cdp_regex, original_cdp_filename, re.IGNORECASE).group(4)
            self.logger.info('Prefixe CDP : ' + cdp_prefix) 
            
            # Get product properties (from configuration)
            product_for_file = product_dict[cdp_prefix]
             
            # Date/Time 
            cdp_time_reseau = cdp_reseau_yyyymmdd + cdp_reseau_hhmm
            cdp_time_reseau_str = self.compute_date_fr(cdp_time_reseau, product_for_file.timezone)
            self.logger.info('Reseau : ' + cdp_time_reseau + ' (' + cdp_time_reseau_str + ')')
            product_for_file.timestamp = cdp_time_reseau
            product_for_file.timestamp_str = cdp_time_reseau_str
              
            # A. Process CDP
            self.logger.info("A. Processus CDP...")
            cdp_status = self.processCdp(product_for_file)
            if not cdp_status:
                return False
            
            # B. Process list reseaux
            self.logger.info("B. Processus Reseaux...")
            reseau_status = self.processReseaux(product_for_file)
            if not reseau_status:
                return False
        
            self.logger.info('Fin carto !')

        except Exception as e:
            # Handle exceptions
            raise Exception(str(e))
            return False
        
        return True

    def processCdp(self, product_for_file):
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
            nb_grains = nb_troncons = 0
            header_nb_grains = header_nb_troncons = 0
            
            data = [l.decode('utf-8') for l in self.cdp.data.splitlines()]
            
            # CSV HEADER (row 1)
            row_header = data[0].split(';')
            header_datetime = row_header[0]
            # - check date
            self.check_cdp_header(header_datetime, product_for_file.timestamp)
            # - get nb grains/troncons
            if provider == 'apic':
                header_nb_grains = int(row_header[1])
            elif provider == 'vf':
                header_nb_troncons = int(row_header[1])
                header_nb_grains = int(row_header[2])
                
            self.logger.info('Nombre de grains attendus : ' + str(header_nb_grains))
            self.logger.info('Nombre de troncons attendus : ' + str(header_nb_troncons))
            # DATA (row 2 to end)
            nb_elements = {"grain":0, "troncon":0}
            for row in data[1:]:
                self.handle_csv_row(row, data_json, product_for_file, nb_elements)
                    
            # Check data integrity
            if not nb_elements['grain'] == header_nb_grains:
                raise Exception('Contenu csv : Nombre de grain incohérent! ' + str(nb_elements['grain']) + ' vs ' + str(header_nb_grains))
            else:
                self.logger.info('Nombre de grains traités : ' + str(nb_elements['grain']))
            if not nb_elements['troncon'] == header_nb_troncons:
                raise Exception('Contenu csv : Nombre de réseau incohérent! ' + str(nb_elements['troncon']) + ' vs ' + str(header_nb_troncons))
            else:
                self.logger.info('Nombre de troncons traités : ' + str(nb_elements['troncon']))
            
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

    def processReseaux(self, produit):
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
            provider = produit.name
            origin = produit.origin 
            output_filename = provider + '_' + origin + '_reseaux.json'
            self.logger.info('Fichier reseau : ' + output_filename)
            file_path = self.dest_path + output_filename
            
            # If file exist, load it
            if os.path.isfile(file_path):
                self.logger.info('Le fichier réseau existe')
                with open(file_path) as json_file:
                    data_json = json.load(json_file)
            
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
            self.logger.info('Le dernier réseau est ' + last_reseau)
            
            # Delete reseau older than 72h (compared to the most recent)
            self.logger.info('Date de dernier réseau : ' + last_reseau)
            datereseau_utc = datetime.strptime(last_reseau, '%Y%m%d%H%M') 
            datereseau_utc_delta_t = datereseau_utc + timedelta(hours=self.delta_t) 
            timestamp_delta_t = datereseau_utc_delta_t.strftime('%Y%m%d%H%M')
            self.logger.info('Date de premier réseau : ' + timestamp_delta_t + ' (' + str(self.delta_t) + 'H)')
            
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

    def handle_csv_row(self, row, data_json, product_for_file, nb_elements):
        """
        Traite les lignes du fichier csv
        :param raw: la ligne de donnée dans le fichier csv
        :param data_json: json de sortie
        :param product_for_file: l'objet produit concerné
        :param nb_elements: compteur nb grains/troncons
        """
        data_row = row.split(';')

        # APIC
        if product_for_file.name == 'apic':
            # grain
            if re.match(self.apic_gr_regex_1, row):
                data_json['communes'].append({'id':data_row[self.apic_pos_gr], 'c:':data_row[self.apic_pos_seuil]})
                grain = str(data_row[self.apic_pos_gr])
                seuil = int(data_row[self.apic_pos_seuil])
                self.compute_dept_list(grain, seuil)
                product_for_file.add_grain(seuil)
                nb_elements["grain"] = nb_elements.get('grain') + 1
            # dept
            elif re.match(self.apic_gr_regex_2, row):
                self.logger.warning('Ligne non traitée: "' + row + '"')
                nb_elements["grain"] = nb_elements.get('grain') + 1
            else:
                raise Exception('Donnée invalide! : ' + row)
        # VF
        elif product_for_file.name == 'vf':   
            # troncon
            if re.match(self.vf_tr_regex, row):
                data_json['troncons'].append({'id':data_row[self.vf_pos_gr], 'c:':data_row[self.vf_pos_seuil]})  
                nb_elements["troncon"] = nb_elements.get('troncon') + 1                       
            # grain
            elif re.match(self.vf_gr_regex, row):
                data_json['communes'].append({'id':data_row[self.vf_pos_gr], 'c:':data_row[self.vf_pos_seuil]})
                grain = str(data_row[self.vf_pos_gr])
                seuil = int(data_row[self.vf_pos_seuil])
                self.compute_dept_list(grain, seuil)
                product_for_file.add_grain(seuil)
                nb_elements["grain"] = nb_elements.get('grain') + 1
            else:
                raise Exception('Donnée invalide! : ' + row)

    def check_cdp_header(self, header_time, cdp_time_reseau):
        """
        Contrôle de l'en-tête du fichier json
        :param header_time: la ligne d'en-tête dans le fichier csv
        :param cdp_time_reseau: heure reseau extraite du nom du fichier
        :return: Exception, si l'horaire du réseau est incohérene
        """
        if header_time == cdp_time_reseau:
            self.logger.info('En-tête csv : Heure reseau valide')
        else:
            raise Exception('En-tête csv : Heure reseau incohérente! ' + header_time + ' vs ' + cdp_time_reseau) 

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
        dept = self.grain_dept_dict.get(grain)
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
        if seuil == -1:
            self.nb_gr_nc += 1
        elif seuil == 1:  
            self.nb_gr_1 += 1
        elif seuil == 2:
            self.nb_gr_2 += 1  
