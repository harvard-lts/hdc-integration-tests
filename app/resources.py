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
        result = {"num_failed": num_failed_tests, "tests_failed": tests_failed}
        dataverse_endpoint = os.environ.get('DATAVERSE_ENDPOINT')
        admin_user_token = os.environ.get('ADMIN_USER_API_TOKEN')

        random_dataverse = {
          "name": "Scientific Research",
          "alias": "science",
          "dataverseContacts": [
            {
              "contactEmail": "pi@example.edu"
            },
            {
              "contactEmail": "student@example.edu"
            }
          ],
          "affiliation": "Scientific Research University",
          "description": "We do all the science.",
          "dataverseType": "LABORATORY"
        }

        random_dataset = {
          "datasetVersion": {
            "metadataBlocks": {
              "citation": {
                "fields": [
                  {
                    "value": "Darwin's Finches",
                    "typeClass": "primitive",
                    "multiple": False,
                    "typeName": "title"
                  },
                  {
                    "value": [
                      {
                        "authorName": {
                          "value": "Finch, Fiona",
                          "typeClass": "primitive",
                          "multiple": False,
                          "typeName": "authorName"
                        },
                        "authorAffiliation": {
                          "value": "Birds Inc.",
                          "typeClass": "primitive",
                          "multiple": False,
                          "typeName": "authorAffiliation"
                        }
                      }
                    ],
                    "typeClass": "compound",
                    "multiple": True,
                    "typeName": "author"
                  },
                  {
                    "value": [
                        { "datasetContactEmail" : {
                            "typeClass": "primitive",
                            "multiple": False,
                            "typeName": "datasetContactEmail",
                            "value" : "finch@mailinator.com"
                        },
                        "datasetContactName" : {
                            "typeClass": "primitive",
                            "multiple": False,
                            "typeName": "datasetContactName",
                            "value": "Finch, Fiona"
                        }
                    }],
                    "typeClass": "compound",
                    "multiple": True,
                    "typeName": "datasetContact"
                  },
                  {
                    "value": [ {
                       "dsDescriptionValue":{
                        "value":   "Darwin's finches (also known as the Galápagos finches) are a group of about fifteen species of passerine birds.",
                        "multiple":False,
                       "typeClass": "primitive",
                       "typeName": "dsDescriptionValue"
                    }}],
                    "typeClass": "compound",
                    "multiple": True,
                    "typeName": "dsDescription"
                  },
                  {
                    "value": [
                      "Medicine, Health and Life Sciences"
                    ],
                    "typeClass": "controlledVocabulary",
                    "multiple": True,
                    "typeName": "subject"
                  }
                ],
                "displayName": "Citation Metadata"
              }
            }
          }
        }

        headers = {"X-Dataverse-key": admin_user_token}

        # Create Dataverse
        create_dataverse = requests.post(
            dataverse_endpoint + '/api/dataverses/root',
            json=random_dataverse,
            headers=headers,
            verify=False)
        json_create_dv = create_dataverse.json()
        if json_create_dv["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Create Dataverse")
            result["Create Dataverse"] = {"status_code": create_dataverse.status_code, "text": json_create_dv["message"]}

        # Create Dataset
        create_dataset = requests.post(
            dataverse_endpoint + '/api/dataverses/science/datasets',
            json=random_dataset,
            headers=headers,
            verify=False)
        json_create_dataset = create_dataset.json()
        if json_create_dataset["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Create Dataset")
            result["Create Dataset"] = {"status_code": create_dataset.status_code, "text": json_create_dataset["message"]}
        dataset_id = json_create_dataset["data"]["id"]
        persistent_id = json_create_dataset["data"]["persistentId"]

        # Publish Dataverse
        publish_dataverse = requests.post(
            dataverse_endpoint
            + '/api/dataverses/science/actions/:publish',
            headers=headers,
            verify=False)
        json_publish_dv = publish_dataverse.json()
        if json_publish_dv["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Publish Dataverse")
            result["Publish Dataverse"] = {"status_code": publish_dataverse.status_code, "text": json_publish_dv["message"]}

        # Publish Dataset
        publish_dataset = requests.post(
            dataverse_endpoint
            + '/api/datasets/:persistentId/actions/:publish?persistentId='
            + persistent_id
            + '&type=major',
            headers=headers,
            verify=False)
        json_publish_dataset = publish_dataset.json()
        if json_publish_dataset["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Publish Dataset")
            result["Publish Dataset"] = {"status_code": publish_dataset.status_code, "text": json_publish_dataset["message"]}

        # Delete Published Dataset
        delete_published_ds = requests.delete(
            dataverse_endpoint + '/api/datasets/' + str(dataset_id) + '/destroy',
            headers=headers,
            verify=False)
        json_delete_published_ds = delete_published_ds.json()
        if json_delete_published_ds["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Delete Published Dataset")
            result["Delete Published Dataset"] = {"status_code": delete_published_ds.status_code, "text": json_delete_published_ds["message"]}

        # Delete Dataverse
        delete_dataverse = requests.delete(
            dataverse_endpoint + '/api/dataverses/science',
            headers=headers,
            verify=False)
        json_delete_dv = delete_dataverse.json()
        if json_delete_dv["status"] != "OK":
            result["num_failed"] += 1
            result["tests_failed"].append("Delete Dataverse")
            result["Delete Dataverse"] = {"status_code": create_dataverse.status_code, "text": json_delete_dv["message"]}

        return json.dumps(result)

# Message listener for transfer-ready queue
