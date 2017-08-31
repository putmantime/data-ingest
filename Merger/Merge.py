import re
from collections import defaultdict

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
        self.merged_record = {
            "id": 'pc/{}'.format(self.resource),
            "id-regex": MergeRecords.key_check(key='@pattern', source=self.ido),
            "id-example": self.generate_example_id(),
            "abbreviation": self.resource,
            "type": MergeRecords.key_check(key='@type', source=self.biop),
            "homepage": MergeRecords.key_check(key='homepage', source=self.obo),
            "description": MergeRecords.key_check(key='definition', source=self.ido),
            "license": MergeRecords.key_check(key='license', source=self.obo),
            "references": self.generate_references(),
            "keywords": self.generate_keywords(),
            "prefixes": self.generate_prefixes(),
            "services": self.generate_services(),
            "datasetIDs": [
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
                        ],
            "URIpatterns": [
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
            ],
            }

    def generate_references(self):
        ido_refs = MergeRecords.key_check(key='documentations', source=self.ido)
        pmids = []
        if ido_refs is not None:
            if not isinstance(ido_refs['documentation'], list):
                if ido_refs['documentation']['@type'] == 'PMID':
                    pmids.append(ido_refs['documentation']['#text'])
            else:
                for ir in ido_refs['documentation']:
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
        service_list = []
        res = service_ele['resource']
        if not isinstance(res, list):
            res = list(res)
        for re in res:
            if not isinstance(re, str):
                service_list.append(
                {
                    "label":re['dataInfo'],
                    "homepage": re['dataResource'],
                    "organization": '',
                    "URIpattern": re['dataEntry'],
                    "contentTypes": ''
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

