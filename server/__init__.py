import os

from flask import Flask, request, json, render_template, jsonify
from config import *
from process.analysis import analysis
from process.dataset import Dataset, args


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/query', methods=['POST'])
    def post():
        req_data = request.get_json()
        json.dump(req_data, open(os.path.join('intermediate/', "query.json"), 'w'))
        data = Dataset(args)
        analysis(data, args)
        # d = {}
        # if ():
        d = {"status": "success"}
        return jsonify(d)

    @app.route('/', methods=['GET'])
    def get():
        return render_template('index.html')

    return app