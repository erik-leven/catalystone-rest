# Catalystone Rest
[![Build Status](https://travis-ci.org/sesam-community/catalystone-rest.svg?branch=master)](https://travis-ci.org/sesam-community/catalystone-rest)

A microservice to connect to catalystones rest interface.

It gives the options of having connections to several different endpoints, catalystone have different tokens and secrets for each of them so specify this in ENV-vars and secrets

##### Example configuration:


```
{
  "_id": "catalystone-rest",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "client_id_org": "$ENV(client_id_org)",
      "client_id_post": "$ENV(client_id_post)",
      "client_id_user": "$ENV(client_id_user)",
      "client_secret_org": "$SECRET(client_secret_org)",
      "client_secret_post": "$SECRET(client_secret_post)",
      "client_secret_user": "$SECRET(client_secret_user)",
      "entities_path_org": "ORGANIZATIONS.ORGANIZATION",
      "entities_path_user": "USERS.USER",
      "get_url": "URL_TO_GET",
      "grant_type": "client_credentials",
      "post_headers": "{'content_type': 'application/json', 'Accept':'application/json'}",
      "post_url": "URL_TO_POST",
      "token_url": "URL_TO_TOKEN"
    },
    "image": "sesamcommunity/catalystone-rest:latest",
    "port": 5000
  }
}

```
