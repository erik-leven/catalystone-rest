from flask import Flask, request, Response
import os
import requests
import logging
import sys
import json

app = Flask(__name__)
logger = None
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('catalystone-service')

# Log to stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)

def get_token(path):
    headers = {}
    logger.info("Creating header")
    if path == "employees" or path == "post_employees":
        headers = {
            "Client-Id":os.environ.get('client_id_user'),
            "Client-Secret":os.environ.get('client_secret_user'),
            "Grant-Type":os.environ.get('grant_type'),
            "Api-Version": os.environ.get('api_version')
        }
    elif path == "user":
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
    else:
        logger.info("undefined path")
        sys.exit()
    resp = requests.get(url=os.environ.get('token_url'), headers=headers)
    if resp.status_code != 200:
        logger.error("Unexpected response status code: %d with response text %s" % (resp.status_code, resp.text))
        raise AssertionError ("Unexpected response status code: %d with response text %s"%(resp.status_code, resp.text))

    if path == "employees" or path == "post_employees":
        token = resp.json()["access_token"]

    else:
        token = resp.json()["response"]["responseMessage"]["access_token"]

    logger.info("Received access token from " + os.environ.get('token_url'))
    return token

class DataAccess:

#main get function check for path and make decisions based on that value
    def __get_all_entities(self, path, query, employeenr):
        if query:
            logger.info("Using query: %s", query)
        token = get_token(path)

        if path == "employees":
            headers= {"Access-Token": token, 
                      "Api-Version": os.environ.get('api_version')}
            if not query:
                if not employeenr:
                    url = os.environ.get('employee_url')
                else:
                    url = os.environ.get('employee_url') + "/" + employeenr
            else:
                url = os.environ.get('employee_url') + query
            logger.info("url = " + url)
        else:
            headers= {'Accept': 'application/json',
                      'content_type': 'application/json'}
            url = os.environ.get('get_url') + "?access_token=" + token

        req = requests.get(url=url, headers=headers)

        if req.status_code != 200:
            logger.error("Unexpected response status code: %d with response text %s" % (req.status_code, req.text))
            raise AssertionError ("Unexpected response status code: %d with response text %s"%(req.status_code, req.text))
        res = req.json()
        if path == "user":
            for entity in res["USERS"]["USER"]:
                yield(entity)
        elif path == "employees":
            for entity in res["employees"]:
                yield(entity)
        elif path == "organization":
            for entity in res["ORGANIZATIONS"]["ORGANIZATION"]:
                yield(entity)
        else:
            logger.info("method not recognized")
        logger.info('Returning entities from %s', path)

    def get_entities(self,path, query, employeenr):
        print("getting all")
        return self.__get_all_entities(path, query, employeenr)

data_access_layer = DataAccess()


def update_entities(entities, headers, counter):
    if counter == 0:
        for entity in entities:
            entity.pop('_id', None)
            response = requests.put(os.environ.get('employee_url'), data=json.dumps(entity), headers=headers)
            if response.status_code is not 200:
                if response.status_code == 403:
                    logger.error("Unexpected response status code: %d with response text %s" % (response.status_code, response.text) + str(counter))
                    raise AssertionError("Unexpected response status code: %d with response text %s" % (response.status_code, response.text) + str(counter))
                logger.error("Got error code: " + str(response.status_code) + " with text: " + response.text + str(counter))
                return Response(response.text, status=response.status_code, mimetype='application/json')
            counter +=1
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    else:
        counter = counter
        for entity in entities[counter:]:
            entity.pop('_id', None)
            response = requests.post(post_url, data=json.dumps(entity), headers=headers)
            if response.status_code is not 200:
                if response.status_code == 403:
                    logger.error("Unexpected response status code: %d with response text %s" % (response.status_code, response.text) + str(counter))
                    raise AssertionError("Unexpected response status code: %d with response text %s" % (response.status_code, response.text), +str(counter))
                logger.error("Got error code: " + str(response.status_code) + " with text: " + response.text + str(counter))
                return Response(response.text, status=response.status_code, mimetype='application/json')
            counter +=1
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

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
    try:    
        s = path.split(";")
        path = s[0]
        query = "?" + s[1]
    except IndexError:
        path = path
        query = False
    try: 
        s = path.split("/")
        path = s[0]
        employeenr = s[1]
    except IndexError:
        path = path
        employeenr = False

    if employeenr != False and query != False:
        logger.error("API does not accept both User identifier field and query. Choose one or the other..")

    if request.method == 'POST':
        access_token = get_token(path)
        entities = request.get_json()
        counter = 0
        headers = {"Access-Token": access_token, "Api-Version": os.environ.get('api_version'), "Content-Type": "application/json"}
        logger.info("Sending entities")
        try:
            return update_entities(entities, headers, counter)

        except Exception as e:
            logger.info(e)
            counter = int(e.args[0].split('}')[-1])
            return update_entities(entities, headers, counter)

    elif request.method == "GET":
        entities = data_access_layer.get_entities(path, query, employeenr)
        return Response(
            stream_json(entities),
            mimetype='application/json'
        )
    else:
        logger.info("undefined request method")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True, port=os.environ.get('port',5000))

