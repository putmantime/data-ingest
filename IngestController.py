from Merger.Source import Source
from Merger.Merge import MergeRecords
from Merger.Agents import normalize_to_list, create_agent_object
import json
import sys
from pprint import pprint
if len(sys.argv) == 0:
    print("""
    please supply a runtype  argument:
    options: ingest or agents

    """)
    sys.exit()

runtype = sys.argv[1].lower()

# Instantiate Source() and retrieve each resource
source_obj = Source()
source_obj.bioportal()
source_obj.identifiers()
source_obj.obo_foundry()

# Generate a list of resource prefixes that can be merged from all 3 sources
databases = source_obj.generate_names_list()
if runtype == 'ingest':
    # Iterate through each source prefix and merge documents
    with open('pc_data.json', 'w') as outfile:
        data = list()
        for database in databases:
            merged = MergeRecords(resource=database,
                                  obo=source_obj.obo_dict[database],
                                  ido=source_obj.ido_dict[database],
                                  biop=source_obj.biop_dict[database])
            data.append(merged.construct_merged_record())
        json.dump(data, outfile)

if runtype == 'agents':

    #  return a list of unique agent objects from identifiers.org
    #  TODO ids still need to be hand minted

    with open('agents.json', 'w') as outfile:
        labels = list()
        data = list()
        for database in databases:
            agents = source_obj.ido_dict[database]['resources']['resource']
            dataResources = normalize_to_list(agents)
            for res in dataResources:
                agent_object = create_agent_object(res=res)
                if agent_object['label'] not in labels:
                    labels.append(agent_object['label'])
                    data.append(agent_object)
        json.dump(data, outfile)


if runtype == 'ping':
    # Iterate through each source prefix and merge documents
    with open('failed_pings.json', 'w') as outfile:
        data = list()
        for database in databases:
            merged = MergeRecords(resource=database,
                                  obo=source_obj.obo_dict[database],
                                  ido=source_obj.ido_dict[database],
                                  biop=source_obj.biop_dict[database])
            record = merged.construct_merged_record()
            data.extend(merged.ping_404)
        json.dump(data, outfile)
