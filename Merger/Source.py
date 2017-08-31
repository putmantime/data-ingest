import urllib.request
import urllib.parse
import xmltodict
import json


class Source(object):
    def __init__(self):
        self.biop_dict = dict()
        self.biop_names = []
        self.ido_dict = dict()
        self.ido_names = []
        self.obo_dict = dict()
        self.obo_names = []

    def bioportal(self):
        """
        retrieve bioportal data
        """
        new_biop = []

        api_key='0a99c359-d2a2-483a-8dca-148c3bb4e8c1'
        params = urllib.parse.urlencode({'apikey': api_key, 'include': 'all'})
        url = "http://data.bioontology.org/ontologies?%s" % params
        with urllib.request.urlopen(url) as f:
            rjson = json.loads(f.read().decode('utf-8'))
            for record in rjson:
                self.biop_dict[record['acronym'].upper()] = record
                self.biop_names.append(record['acronym'].upper())
        return

    def identifiers(self):
        """
        retrieve identifiers.org data
        """
        new_id = []
        id_url='http://www.ebi.ac.uk/miriam/main/export/'
        file_name='xml'
        opener = urllib.request.urlretrieve(id_url+file_name, filename=file_name)
        x2j = Source.xml2dict(file_name)
        for record in x2j['miriam']['datatype']:
            self.ido_dict[record['namespace'].upper()] = record
            self.ido_names.append(record['namespace'].upper())
        return

    def obo_foundry(self):
        """
        retrieve obo foundry data
        """
        new_obo = []
        base_url='http://www.obofoundry.org/registry/ontologies.jsonld'
        with urllib.request.urlopen(base_url) as url:
            data = json.loads(url.read().decode())
            for record in data['ontologies']:
                self.obo_dict[record['id'].upper()] = record
                self.obo_names.append(record['id'].upper())
        return

    def generate_names_list(self):
        """
        generate list of common names from all 3 resources
        """
        return list(set(self.obo_names) & set(self.biop_names) & set(self.ido_names))

    @staticmethod
    def xml2dict(xml_file, xml_attribs=True):
        """
        converts xml to python dictionary
        """
        with open(xml_file, "rb") as f:
            d = xmltodict.parse(f, xml_attribs=xml_attribs)
            return d
