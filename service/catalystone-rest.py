import os
import requests
import logging
import sys
from time import sleep
import dotdictify

logger = None
update_interval = 84600

##getting token
def get_token():
    logger.info("Creating header")
    headers = {
        "client_id":os.environ.get('client_id'),
        "client_secret":os.environ.get('client_secret'),
        "grant_type":os.environ.get('grant_type')
    }
    resp = requests.get(url=os.environ.get('url'), headers=headers).json()
    token = dotdictify.dotdictify(resp).response.responseMessage.access_token
    logger.info("Received access token from " + os.environ.get('url'))
    return token

def str_to_bool(string_input):
    return str(string_input).lower() == "true"

def get(path):
    entities = data_access_layer.get_paged_entities(path)
    return Response(
        stream_json(entities),
        mimetype='application/json'
    )

@app.route("/user", methods=["GET"])
def get_user():
    token = get_token(os.environ.get('url'))
    entities = data_access_layer.get_token(token)
    return Response(
        stream_json(entities),
        mimetype='application/json'
    )

@app.route("/organisation", methods=["GET"])
def get_cv():
    path = os.environ.get("user_url")
    entities = data_access_layer.get_cvs(path)
    return Response(
        stream_json(entities),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
