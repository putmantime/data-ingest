import re
from collections import defaultdict, OrderedDict
import requests

__author__ = 'timputman'


class MergeRecords(object):
    """
    input:  resource= a resource prefix
            records from Source(object):
                obo= obo record
                ido= identifiers.org record
                biop= bioportal record
    returns: merged record that fits the prefixcommons schema
                https://github.com/prefixcommons/data-ingest/blob/master/prefixcommons.schema.json
    """
    def __init__(self, resource, obo, ido, biop):
        self.resource = resource
        self.obo = obo
        self.ido = ido
        self.biop = biop
        self.is_prefixed = False
        self.regex = self.generate_regex()
        self.ping_404 = list()

    def construct_merged_record(self):
        merged_record = OrderedDict()
        merged_record["id"] = self.generate_pc_id()
        merged_record["type"] = self.generate_type()
        merged_record["label"] = self.generate_label()
        merged_record["abbreviation"] = self.resource
        merged_record['homepage'] = self.generate_homepage()
        merged_record["authority"] = None  # once agent ids are handcurated/minted and mapped to prefixes, this can be done
        merged_record["license"] = self.generate_license()
        merged_record["documentation"] = None # the exemplar record points to a help page on the go website, don't have a programatic way to determine this now
        merged_record["references"] = self.generate_references()
        merged_record["keywords"] = self.generate_keywords()
        merged_record["prefixes"] = self.generate_prefixes()
        merged_record["description"] = MergeRecords.key_check(key='definition', source=self.ido)
        merged_record['datasetIDs'] = [
                          {
                            "id": self.ido['uris']['uri'][1]['#text'],
                            "authority": {
                              "id": "org/id.org"
                            }
                          },
                          {
                            "id": MergeRecords.key_check(key='@id', source=self.biop),
                            "authority": {
                              "id": "org/bioportal"
                            }
                          },
                          {
                            "id": MergeRecords.key_check(key='ontology_purl', source=self.obo),
                            "authority": {
                              "id": "org/obofoundry"
                            }
                          }
                        ]
        merged_record["id-regex"] = self.regex
        merged_record["id-example"] = self.generate_example_id()
        merged_record['URIpatterns'] = [
                {
                    "URIpattern": "http://purl.obolibrary.org/obo/%s_${id}" % (self.resource.lower()),
                    "usedBy": [
                        {"id":"org/obofoundry"}
                    ]
                },
                {
                    "URIpattern": "%s${id}" % (self.generate_ido_uri()),
                    "usedBy": [
                      {"id":"org/id.org"}
                    ]
                },
                {
                    "URIpattern": "http://purl.obolibrary.org/obo/%s_${id}" % (self.resource),
                    "usedBy": [
                      {"id":"org/bioportal"}
                    ]
                },
            ]
        merged_record["services"] = self.generate_services()

        return merged_record
    
    def generate_regex(self):
        """
        from regex, determine if prefixed, and which delimeter is used
        """
        ido_regex = MergeRecords.key_check(key='@pattern', source=self.ido)
        if self.resource in ido_regex:
            self.is_prefixed = True    
        return ido_regex
    
    def generate_pc_id(self):
        """
        using the prefix as placeholder, will need to use numerical ids minted by PC eventually
        """
        return 'pc/{}'.format(self.resource)
    
    def generate_type(self):
        """
        bioportal seems to be the only resources that provides a type 
        """
        biop_type = MergeRecords.key_check(key='@type', source=self.biop)
        return biop_type

    def generate_label(self):
        """
        all three resources have labels, but many don't agree.
        this method only returns the identifiers.org label for now
        """
        obo_label = MergeRecords.key_check(key='title', source=self.obo)
        ido_label = MergeRecords.key_check(key='name', source=self.ido)
        biop_label = MergeRecords.key_check(key='name', source=self.biop)
        return ido_label
    
    def generate_license(self):
        """
        obofoundery seems to be the only resources that provides a license 
        """
        obo_license = MergeRecords.key_check(key='license', source=self.obo)
        if obo_license is not None:
            return obo_license['url']
        else:
            return obo_license
    
    def generate_homepage(self):
        """
        obofoundry has homepage for some records
        """
        return MergeRecords.key_check(key="homepage", source=self.obo)

    def generate_references(self):
        """
        
        """
        ido_refs = MergeRecords.key_check(key='documentations', source=self.ido)
        pmids = []
        if ido_refs is not None:
            documentation = MergeRecords.normalize_to_list(ido_refs['documentation'])
            for ir in documentation:
                if ir['@type'] == 'PMID':
                    pmids.append(ir['#text'])
        purls = ['https://www.ncbi.nlm.nih.gov/pubmed/{}'.format(x.split(':')[-1])
                 for x in pmids]
        return purls

    def generate_keywords(self):
        kw = MergeRecords.key_check(key='tags', source=self.ido)
        if kw is not None:
            return kw['tag']
        else:
            return None

    def generate_services(self):
        service_ele = MergeRecords.key_check(key='resources', source=self.ido)
        service_list = list()
        servs = MergeRecords.normalize_to_list(service_ele['resource'])
 
        for serv in servs:
            if not isinstance(serv, str):
                dataEntry = serv['dataEntry']
                prefixDelimeter = re.split(r'(\d+)', serv['dataEntityExample'])
                serv_prefix = prefixDelimeter[0]
                URIpattern = None
                
                if self.is_prefixed is True:
                    exploded_url = dataEntry.split('$id')
                    URIpattern = exploded_url[0] + serv_prefix + '$id'
                else:
                    URIpattern = serv['dataEntry']
                    
                ping_url = serv['dataEntry'].replace('$id', serv['dataEntityExample'])
                status = MergeRecords.ping_service(ping_url)
                if status == 404:
                    self.ping_404.append({'URIpattern': URIpattern, 'URIexample': ping_url})
                service_list.append(
                    {
                        "label":serv['dataInfo'],
                        "homepage": serv['dataResource'],
                        "organization": '', # agent id key, value pair onces it has been curated and mapped
                        "URIpattern": URIpattern,
                        "contentTypes": '' # don't have a programmatic source for these
                    }
                )
                
        return service_list

    def generate_prefixes(self):
        prefix_list = [
            {
                'prefix': self.ido['namespace'],
                'used_by': {"id": "org/id.org"}
            },
            {
                'prefix': self.obo['id'],
                'used_by': {"id": "org/obofoundry"}
            },
            {
                'prefix': self.biop['@id'].split('/')[-1],
                'used_by': {"id": "org/bioportal"}
            }
        ]

        d = defaultdict(list)

        for pre in prefix_list:
            d[pre['prefix']].append(pre['used_by'])
        prefix_final = []
        for key in d:
            preObj = {
                'label': key,
                'usedBy': d[key]
            }
            prefix_final.append(preObj)
        return prefix_final

    def generate_ido_uri(self):
        uris = self.ido['uris']['uri']
        for uri in uris:
            if uri['@type'] == 'URL':
                if '@deprecated' not in uri.keys():
                    return uri['#text']

    def generate_prefix_map(self, key):
        pref_map = {
            'prefix': self.resource,
            'identifiers.org': MergeRecords.key_check(key=key, source=self.ido),
            'bioportal': MergeRecords.key_check(key=key, source=self.biop),
            'obo_foundry': MergeRecords.key_check(key=key, source=self.obo)
        }
        return pref_map

    def generate_dataEntry_field(self):
        resources = MergeRecords.key_check(key='resources', source=self.ido)
        resource_list = []
        if resources is not None:
            resources = self.ido['resources']['resource']
            for resource in resources:
                if not isinstance(resource,str):
                    resource_list.append(resource['dataEntry'])
        return resource_list

    def generate_example_id(self):
        resources = MergeRecords.key_check(key='resources', source=self.ido)
        example_list = []
        if resources is not None:
            resources = self.ido['resources']['resource']
            for resource in resources:
                if isinstance(resource,str):
                    example_list.append(resources['dataEntityExample'])
                else:
                    if '@obsolete' in resource.keys():
                        break
                    else:
                        example_list.append(resource['dataEntityExample'])
        newset = (set(example_list))
        newlist = [self.resource]
        for item in newset:
            newlist.append(item)

        if len(example_list) > 0:
            fobj = re.split(r'(\d+)', example_list[0])
            if len(fobj) > 1:
                return fobj[1]
        else:

            return None

    @staticmethod
    def key_check(key, source):
        if key in source.keys():
            return source[key]
        else:
            return None
        
    @staticmethod
    def normalize_to_list(var):
        record_list = list()
        if not isinstance(var, list):
            record_list.append(var)
        else:
            record_list.extend(var)
        return record_list
    
    @staticmethod
    def ping_service(url):
        try:
            r = requests.get(url, timeout=20)
            return r.status_code
        except Exception as e:
            return 'TO'

