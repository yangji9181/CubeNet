import os

def data_config(args, dataset='dblp'):
    print('here')
    args['data_dir'] = 'data/'
    args['data_name'] = dataset
    args['meta_file'] = args['data_dir'] + args['data_name'] + '/' + 'meta.dat'
    args['node_file'] = args['data_dir'] + args['data_name'] + '/' + 'node.dat'
    args['link_file'] = args['data_dir'] + args['data_name'] + '/' + 'link.dat'
    args['label_file'] = args['data_dir'] + args['data_name'] + '/' + 'label.dat'
    args['init_file'] = args['data_dir'] + args['data_name'] + '/' + 'init.dat'

    inter_data = 'intermediate/data.pickle'
    if os.path.exists(inter_data):
        os.remove(inter_data)


args = {}
args['meta_json'] = 'intermediate/meta.json'
args['query_json'] = 'intermediate/query.json'
args['data_pickle'] = 'intermediate/data.pickle'