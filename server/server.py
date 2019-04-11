import os

from flask import Flask, request, json, render_template, jsonify

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def post():
    req_data = request.get_json()
    print("req_data" + str(req_data))
    print(req_data)

    # from server.process.test_import import Dataset
    # data = Dataset()
    # data.test_func()
    # with open(os.path.join('intermediate/', 'short_text.txt')) as f:
    #     print(f)
    # # return "hi from server"
    #
    json.dump(req_data['query'], open(os.path.join('intermediate/', 'query.json'), 'w'))
    from server.process.dataset import Dataset
    from server.process.config import args
    data = Dataset(args)
    from server.process.analysis import analysis
    analysis(data, args)
    d = {"status": "success"}

    print('success return')
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