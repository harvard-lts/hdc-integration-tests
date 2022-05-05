import time
import stomp

import requests, datetime
from flask_restx import Resource, Api
from flask import render_template
import os, json

from stomp.utils import Frame

test_message_received = False
# Possibly try removing and see if it works
test_message_content = ""

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

    @app.route('/apps/healthcheck')
    def app_healthchecks():
        num_failed_tests = 0
        tests_failed = []
        result = {"num_failed": num_failed_tests, "tests_failed": tests_failed}

        # Health Check Tests for DIMS
        health = requests.get(os.environ.get('DIMS_ENDPOINT') + '/health', verify=False)
        if health.status_code != 200:
            result["num_failed"] += 1
            result["tests_failed"].append("DIMS healthcheck")
            result["DIMS"] = {"status_code": health.status_code, "text": health.text}

        # Health Check Tests for DTS
        # TODO: status_code for DTS is 404, although the health check is successful
        health = requests.get(os.environ.get('DTS_ENDPOINT') + '/healthcheck', verify=False)
        json_health = json.loads(health.text)
        if json_health["status"] != "success":
            result["num_failed"] += 1
            result["tests_failed"].append("DTS healthcheck")
            result["DTS"] = {"status_code": health.status_code, "text": health.text}

        return json.dumps(result)

    @app.route('/DIMS/DVIngest')
    def dims_ingest_dv():
        num_failed_tests = 0
        tests_failed = []
        result = {"num_failed": num_failed_tests, "tests_failed": tests_failed, "info": {}}
        dataverse_endpoint = os.environ.get('DATAVERSE_ENDPOINT')
        admin_user_token = os.environ.get('ADMIN_USER_API_TOKEN')

        app.logger.debug("Loading dataset dictionary")
        with open('/home/appuser/test_data/dataset-finch1.json') as dataset:
            data = dataset.read()

        # reconstructing the data as a dictionary
        random_dataset = json.loads(data)

        headers = {"X-Dataverse-key": admin_user_token}

        # # Connect to transfer-ready queue
        # connection = create_mq_connection()
        # connection.set_listener('', TestConnectionListener())

        time.sleep(5.0)

        app.logger.debug("Creating dataset")
        # Create Dataset
        create_dataset = requests.post(
            dataverse_endpoint + '/api/dataverses/archived/datasets',
            json=random_dataset,
            headers=headers,
            verify=False)
        json_create_dataset = create_dataset.json()
        if json_create_dataset["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Create Dataset")
            result["Failed Create Dataset"] = {"status_code": create_dataset.status_code, "text": json_create_dataset["message"]}
        dataset_id = json_create_dataset["data"]["id"]
        persistent_id = json_create_dataset["data"]["persistentId"]
        result["info"]["persistentId"] = persistent_id
        result["info"]["datasetId"] = dataset_id
        result["info"]["Create Dataset"] = {"status_code": create_dataset.status_code}

        app.logger.debug("Publishing dataset")
        # Publish Dataset
        publish_dataset = requests.post(
            dataverse_endpoint
            + '/api/datasets/:persistentId/actions/:publish?persistentId='
            + persistent_id
            + '&type=major'
            + '&assureIsIndexed=true',
            headers=headers,
            verify=False)
        json_publish_dataset = publish_dataset.json()

        # Wait for changes to take effect
        while publish_dataset.status_code != 200 and json_publish_dataset["message"] == "Dataset is awaiting indexing":
            app.logger.debug("Waiting in while loop dataset")
            time.sleep(3.0)
            publish_dataset = requests.post(
                dataverse_endpoint
                + '/api/datasets/:persistentId/actions/:publish?persistentId='
                + persistent_id
                + '&type=major'
                + '&assureIsIndexed=true',
                headers=headers,
                verify=False)
            json_publish_dataset = publish_dataset.json()

        if json_publish_dataset["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Publish Dataset")
            result["Failed Publish Dataset"] = {"status_code": publish_dataset.status_code, "text": json_publish_dataset["message"]}
        result["info"]["Publish Dataset"] = {"status_code": publish_dataset.status_code}

        # Another wait for safe measure
        time.sleep(3.0)

        # await_until_message_received_or_timeout()
        #
        # if not test_message_received:
        #     result["num_failed"] += 1
        #     result["tests_failed"].append("Message Received Not in Queue")
        # else:
        #     result["info"]["Message Received in Queue"] = "Message Received!" # test_message_content

        # app.logger.debug("Delete dataset")
        # # Delete Published Dataset
        # delete_published_ds = requests.delete(
        #     dataverse_endpoint + '/api/datasets/' + str(dataset_id) + '/destroy',
        #     headers=headers,
        #     verify=False)
        # json_delete_published_ds = delete_published_ds.json()
        # if json_delete_published_ds["status"] != "OK":
        #     result["num_failed"] += 1
        #     result["tests_failed"].append("Delete Published Dataset")
        #     result["Failed Delete Published Dataset"] = {"status_code": delete_published_ds.status_code, "text": json_delete_published_ds["message"]}
        # result["info"]["Delete Published Dataset"] = {"status_code": delete_published_ds.status_code}

        return json.dumps(result)

    def create_mq_connection() -> stomp.Connection:
        mq_host = os.getenv('MQ_TRANSFER_HOST'),
        mq_port = os.getenv('MQ_TRANSFER_PORT'),
        mq_user = os.getenv('MQ_TRANSFER_USER'),
        mq_password = os.getenv('MQ_TRANSFER_PASSWORD')

        connection = stomp.Connection(
            host_and_ports=[(mq_host, mq_port)],
            heartbeats=(40000, 40000),
            keepalive=True
        )

        connection.set_ssl([(mq_host, mq_port)])

        connection.connect(
            mq_user,
            mq_password,
            wait=True
        )

        return connection

    def await_until_message_received_or_timeout() -> None:
        timeout = time.time() + 30
        while not test_message_received and time.time() < timeout:
            time.sleep(1)

class TestConnectionListener(stomp.ConnectionListener):
    def on_message(self, frame: Frame) -> None:
        global test_message_received
        # global test_message_content
        test_message_received = True
        # test_message_content = frame.body

# Message listener for transfer-ready queue
# Add files to Ansible for dev, qa deploys

# Check S3 for export - delete after verified
