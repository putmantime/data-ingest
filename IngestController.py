from Merger.Source import Source
from Merger.Merge import MergeRecords
import json

# Instantiate Source() and retrieve each resource
source_obj = Source()
source_obj.bioportal()
source_obj.identifiers()
source_obj.obo_foundry()

# Generate a list of resource prefixes that can be merged from all 3 sources
databases = source_obj.generate_names_list()

# Iterate through each source prefix and merge documents

with open('pc_data.json', 'w') as outfile:
    data = []
    for database in databases:
        merged = MergeRecords(resource=database,
                              obo=source_obj.obo_dict[database],
                              ido=source_obj.ido_dict[database],
                              biop=source_obj.biop_dict[database])
        data.append(merged.merged_record)
    json.dump(data, outfile)
