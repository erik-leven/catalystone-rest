from flask import Flask, request, Response
import os
import requests
import logging
import sys
import json
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
    headers = {}
    logger.info("Creating header")

    if path == "user":
        headers = {
            "client_id":os.environ.get('client_id_user'),
            "client_secret":os.environ.get('client_secret_user'),
            "grant_type":os.environ.get('grant_type')
        }
    elif path == "organization":
        headers = {
            "client_id":os.environ.get('client_id_org'),
            "client_secret":os.environ.get('client_secret_org'),
            "grant_type":os.environ.get('grant_type')
        }
    elif path == "post_user":
        headers = {
            "client_id": os.environ.get('client_id_post'),
            "client_secret": os.environ.get('client_secret_post'),
            "grant_type": os.environ.get('grant_type')
        }
    else:
        logger.info("undefined method")
        sys.exit()

    resp = requests.get(url=os.environ.get('token_url'), headers=headers).json()
    token = dotdictify.dotdictify(resp).response.responseMessage.access_token
    logger.info("Received access token from " + os.environ.get('token_url'))
    return token

class DataAccess:

#main get function check for path and make decisions based on that value
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

# stream entities
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

@app.route("/<path:path>", methods=["GET", "POST"])
def get_path(path):

    if request.method == 'POST':
        post_url = os.environ.get('post_url') + "?access_token=" + get_token(path)
        logger.info(request.get_json())
        entities = request.get_data()
                #logger.info(json.dumps(json.loads(entities)))
        headers = json.loads(os.environ.get('post_headers').replace("'", "\""))

        logger.info("Sending entities")
        try:
            return update_entities(entities, headers, post_url)

        except Exception as e:
            logger.info(e)
            if e == "error token":
                post_url = os.environ.get('post_url') + "?access_token=" + get_token(path)
                return update_entities(entities, headers, post_url)


    elif request.method == "GET":
        path = path

    else:
        logger.info("undefined request method")

        entities = data_access_layer.get_entities(path)
        return Response(
            stream_json(entities),
            mimetype='application/json'
        )


def update_entities(entities, headers, post_url):
    for entity in json.loads(entities):
        logger.info(str(entity))
        response = requests.post(post_url, data=json.dumps(entity), headers=headers)
        if response.status_code is not 200:
            logger.error("Got error code: " + str(response.status_code) + "with text: " + response.text)
            return Response(response.text, status=response.status_code, mimetype='application/json')
        logger.info("Prosessed " + str(entity))
    return Response("done", status=response.status_code, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))
