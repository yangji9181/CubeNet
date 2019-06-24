import os

from flask import Flask, request, json, render_template, jsonify
from server.process.dataset import Dataset, initialization
from server.process.analysis import exploration, properties, patterns, cell_color

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get():
    print("Initialization success!")
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init():
    req_data = request.get_json()
    obj = initialization(req_data['dataset'])
    print(obj)
    return jsonify(obj)

@app.route('/query', methods=['POST'])
def query():
    req_data = request.get_json()
    query = req_data['query']
    from server.process.config import args
    json.dump(query,
              open(args['query_json'], 'w'),
              indent=4,
              separators=(',', ': '))
    from server.process.dataset import Dataset
    data = Dataset(args)
    network = exploration(req_data['query'], data)
    cube = cell_color(req_data['query'], data)
    cube_net = {'network': network, 'cube': cube}
    return jsonify(cube_net)

@app.route('/contrast', methods=['POST'])
def contrast():
    req_data = request.get_json()
    results = properties(req_data['node'])
    return jsonify(results)

@app.route('/pattern', methods=['POST'])
def pattern():
    req_data = request.get_json()
    results = patterns(req_data['node'])
    return jsonify(results)

if __name__ == '__main__':
   app.run(debug = True)