import os

from flask import Flask, request, json, render_template, jsonify
from server.process.dataset import Dataset
from server.process.config import data_config
from server.process.analysis import exploration, properties, patterns

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get():
    print("Initialization success!")
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def post():
    req_data = request.get_json()
    query = req_data['query']
    from server.process.config import args
    data_config(args, query['dataset'])
    json.dump(query, open(args['query_json'], 'w'))
    data = Dataset(args)
    network = exploration(req_data['query'], data)
    return jsonify(network)

@app.route('/contrast', methods=['POST'])
def contrast():
    req_data = request.get_json()
    results = properties(req_data['node'])
    return jsonify(results)


if __name__ == '__main__':
   app.run(debug = True)