import requests
from flask_restx import Resource, Api
from flask import render_template
import os, json

def define_resources(app):
    api = Api(app, version='1.0', title='HDC Integration Tests', description='This project contains the integration tests for the HDC project')
    dashboard = api.namespace('/', description="This project contains the integration tests for the HDC project")

    # Heartbeat/health check route
    @dashboard.route('/version', endpoint="version", methods=['GET'])
    class Version(Resource):
        def get(self):
            version = os.environ.get('APP_VERSION', "NOT FOUND")
            return {"version": version}
    @app.route('/hello-world')
    def hello_world():
        return render_template('index.html')

    @app.route('/dev/health')
    def healthcheck_dev():
        num_failed_tests = 0
        tests_failed = []
        result = {"num_failed": num_failed_tests, "tests_failed": tests_failed}

        # Health Check Tests for DIMS
        health = requests.get(os.environ.get('DIMS_DEV_ENDPOINT') + '/health', verify=False)
        if health.status_code != 200:
            result["num_failed"] += 1
            result["tests_failed"].append("DIMS healthcheck Dev")
            result["DIMS"] = {"status_code": health.status_code, "text": health.text}

        # Health Check Tests for DTS
        # TODO: status_code for DTS is 404, although the health check is successful
        health = requests.get(os.environ.get('DTS_DEV_ENDPOINT') + '/healthcheck', verify=False)
        json_health = json.loads(health.text)
        if json_health["status"] != "success":
            result["num_failed"] += 1
            result["tests_failed"].append("DTS healthcheck Dev")
            result["DTS"] = {"status_code": health.status_code, "text": health.text}

        return json.dumps(result)

    @app.route('/qa/health')
    def healthcheck_qa():
        num_failed_tests = 0
        tests_failed = []
        result = {"num_failed": num_failed_tests, "tests_failed": tests_failed}

        # Health Check Tests for DIMS
        health = requests.get(os.environ.get('DIMS_QA_ENDPOINT') + '/health', verify=False)
        if health.status_code != 200:
            result["num_failed"] += 1
            result["tests_failed"].append("DIMS healthcheck QA")
            result["DIMS"] = {"status_code": health.status_code, "text": health.text}

        # Health Check Tests for DTS
        health = requests.get(os.environ.get('DTS_QA_ENDPOINT') + '/healthcheck', verify=False)
        json_health = json.loads(health.text)
        if json_health["status"] != "success":
            result["num_failed"] += 1
            result["tests_failed"].append("DTS healthcheck QA")
            result["DTS"] = {"status_code": health.status_code, "text": health.text}

        return json.dumps(result)