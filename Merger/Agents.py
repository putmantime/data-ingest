def normalize_to_list(var):
    record_list = list()
    if not isinstance(var, list):
        record_list.append(var)
    else:
        record_list.extend(var)
    return record_list


def create_agent_object(res):
    agent_record = dict()
    agent_record['id'] = 'org/{}'.format(None)  # leaving blank, will be minted by hand
    agent_record['homepage'] = res['dataResource']
    agent_record['label'] = res['dataInfo']
    agent_record['institution']  =res['dataInstitution']
    return agent_record
