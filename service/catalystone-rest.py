from flask import Flask, request, Response
import os
import requests
import logging
import sys
import json
from time import sleep
import dotdictify

app = Flask(__name__)
logger = None
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('catalystone-service')

# Log to stdout

stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)

##getting token
def get_token(path):
    logger.info("Creating header")
    if path == "user":
        headers = {
            "client_id":os.environ.get('client_id_user'),
            "client_secret":os.environ.get('client_secret_user'),
            "grant_type":os.environ.get('grant_type')
        }
    if path == "organization":
        headers = {
            "client_id":os.environ.get('client_id_org'),
            "client_secret":os.environ.get('client_secret_org'),
            "grant_type":os.environ.get('grant_type')
        }
    else:
        logger.info("undefined method")
        sys.exit()
    resp = requests.get(url=os.environ.get('token_url'), headers=headers).json()
    token = dotdictify.dotdictify(resp).response.responseMessage.access_token
    logger.info("Received access token from " + os.environ.get('token_url'))
    return token

class DataAccess:

#main get function, will probably run most via path:path
    def __get_all_entities(self, path):
        logger.info("Fetching data from url: %s", path)
        token = get_token(path)
        headers= {'Accept': 'application/json',
                  'content_type': 'application/json'}
        url = os.environ.get('get_url') + "?access_token=" + token
        logger.info("Fetching data from url: %s", path)
        req = requests.get(url, headers=headers)

        if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError ("Unexpected response status code: %d with response text %s"%(req.status_code, req.text))
        res = dotdictify.dotdictify(json.loads(req.text))
        if path == "user":
            for entity in res.get(os.environ.get("entities_path_user")):

                yield(entity)
        if path == "organization":
            for entity in res.get(os.environ.get("entities_path_org")):
                yield (entity)
        else:
            logger.info("method not recognized")
        logger.info('Returning entities from %s', path)

    def get_entities(self,path):
        print("getting all")
        return self.__get_all_entities(path)

data_access_layer = DataAccess()


def stream_json(clean):
    first = True
    yield '['
    for i, row in enumerate(clean):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'

# @app.route("/user", methods=["GET"])
# def get_user():
#     path = os.environ.get("user_url")
#     entities = data_access_layer.get_entities(path)
#     return Response(
#         stream_json(entities),
#         mimetype='application/json'
#     )
#
# @app.route("/organisation", methods=["GET"])
# def get_organisation():
#     path = os.environ.get("org_url")
#     entities = data_access_layer.get_entities(path)
#     return Response(
#         stream_json(entities),
#         mimetype='application/json'
#     )

@app.route("/<path:path>", methods=["GET", "POST"])
def get_path(path):
    if request.method == "POST":
        path = request.get_json()
    if request.method == "GET":
        path = path

    entities = data_access_layer.get_entities(path)
    return Response(
        stream_json(entities),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
