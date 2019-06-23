def data_config(data_name):
    argsDict = {}
    argsDict['meta_json'] = 'intermediate/meta.json'
    argsDict['pickle_file'] = 'intermediate/data.pickle'

    argsDict['data_dir'] = 'data/'
    argsDict['data_name'] = data_name
    argsDict['meta_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + 'meta.dat'
    argsDict['node_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + 'node.dat'
    argsDict['link_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + 'link.dat'
    argsDict['label_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + 'label.dat'

    return argsDict