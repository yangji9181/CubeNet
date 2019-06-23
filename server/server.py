import os

from flask import Flask, request, json, render_template, jsonify
from server.process.dataset import Dataset
from server.process.config import data_config
from server.process.analysis import exploration

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get():
    print("Initialization success!")
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def post():
    req_data = request.get_json()
    query = req_data['query']
    dataname = query['dataset']
    args = data_config(dataname)
    data = Dataset(args)
    network = exploration(req_data['query'], data)
    return jsonify(network)

@app.route('/contrast', methods=['POST'])
def contrast():
    '''
    take: {"node": "x"}
    :return: {'type': {'property1': {'label1' : x, 'label2': x}, 'property2': {'label1' : x, 'label2': x}}
    '''
    # read contrast index
    req_data = request.get_json()
    sub_type = req_data['node']
    # print (req_data)
    # print (sub_type)
    # get meta file in order to know index meaning
    meta = open(os.path.join('intermediate/', 'meta.json'), 'r')
    meta = json.load(meta)

    # get type name
    type_name = meta['node'][sub_type]

    # get current full graph
    cur_query = open(os.path.join('intermediate/', 'query.json'), 'r')
    cur_query = json.load(cur_query)
    # get contrast label list
    if sub_type in cur_query['filters']:
        iter_list = cur_query['filters'][sub_type]
    else:
        iter_list = meta['label'][sub_type].keys()
        cur_query['filters'][sub_type] = iter_list

    # setup parameters
    from server.process.dataset import Dataset
    from server.process.config import args, make_dir
    data_name_record = open('intermediate/dataname.txt', 'r')
    for line in data_name_record:
        data_name = line
        break
    data_name_record.close()
    make_dir(data_name)
    data = Dataset(args)

    # setup return result
    res_dict = {}
    # res_dict[type_name] = {}
    # res_dict[type_name]['radius'] = {}
    # res_dict[type_name]['diameter'] = {}
    # res_dict[type_name]['density'] = {}

    res_dict['node_type'] = type_name
    res_dict['properties'] = []
    res_dict['properties'].append({})
    res_dict['properties'].append({})
    res_dict['properties'].append({})
    res_dict['properties'][0]['name'] = 'radius'
    res_dict['properties'][0]['labels'] = []
    res_dict['properties'][1]['name'] = 'diameter'
    res_dict['properties'][1]['labels'] = []
    res_dict['properties'][2]['name'] = 'density'
    res_dict['properties'][2]['labels'] = []

    # get property for each sub-graph
    cur = 0
    for item in iter_list:
        cur_dict = cur_query.copy()
        cur_dict['filters'][sub_type] = []
        cur_dict['filters'][sub_type].append(item)
        json.dump(cur_dict, open(os.path.join('intermediate/', 'contrast_q.json'), 'w'))
        from server.process.contrast import analysis
        analysis(data, args)
        from server.process.get_networkx import get_graph_property
        t = get_graph_property(args['contrast_n'])
        label = meta['label'][sub_type][item][0]
        # res_dict[type_name]['radius'][label] = t[0]
        # res_dict[type_name]['diameter'][label] = t[1]
        # res_dict[type_name]['density'][label] = t[2]
        for i in range(3):
            res_dict['properties'][i]['labels'].append({})
            res_dict['properties'][i]['labels'][cur]['name'] = label
            res_dict['properties'][i]['labels'][cur]['val'] = t[i]
        cur += 1
    json.dump(res_dict, open(os.path.join('intermediate/', 'histogram_res.json'), 'w'))
    print ('success')
    return jsonify(res_dict)

if __name__ == '__main__':
   app.run(debug = True)