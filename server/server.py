import os

from flask import Flask, request, json, render_template, jsonify

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def post():
    req_data = request.get_json()
    print("req_data" + str(req_data))
    print(req_data)

    json.dump(req_data['query'], open(os.path.join('../intermediate/', 'query.json'), 'w'))
    from process.dataset import Dataset
    from process.config import args
    data = Dataset(args)
    from process.analysis import analysis
    analysis(data, args)
    d = {"status": "success"}
    return jsonify(d)

# @app.route('/test', methods=['POST', 'GET'])
# def test():
#     req_data = request.get_json(force=True)
#     print("req_data" + str(request.data))
#     print("from test")
#     return "success"

@app.route('/', methods=['GET'])
def get():
    print("get!!")
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug = True)