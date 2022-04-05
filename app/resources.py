from flask_restx import Resource, Api
from flask import request, current_app, make_response, jsonify, render_template
import os, json

# Import custom class files here
#from . import <class> <class>

def define_resources(app):
    api = Api(app, version='1.0', title='Docker Flask Template', description='This project will create a generic, Dockerized, Flask application ready for action!')
    dashboard = api.namespace('/', description="This project will create a generic, Dockerized, Flask application ready for action!")

    # Heartbeat/health check route
    @dashboard.route('/version', endpoint="version", methods=['GET'])
    class Version(Resource):
        def get(self):
            version = os.environ.get('APP_VERSION', "NOT FOUND")
            return {"version": version}
    @app.route('/hello-world')
    def hello_world():
        return render_template('index.html')