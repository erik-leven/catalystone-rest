# Catalystone Rest
[![Build Status](https://travis-ci.org/sesam-community/catalystone-rest.svg?branch=master)](https://travis-ci.org/sesam-community/catalystone-rest)

A microservice to connect to catalystones rest interface

##### Example configuration:


```
{
  "_id": "catalystone-rest",
  "type": "system:microservice",
  "docker": {
    "environment": {
      
      "url": "http://token_url.com",
      # optional values below
      "use_header": "True",
      "verify_ssl": "False" (verfy ssl to node. Defaults to true),
      "client_id": "provided client id",
      "client_secret": "provided secret"

    },
    "image": "sesamcommunity/catalystone-rest:latest",
    "port": 5000
  }
}

```

If use_header is set to false you will need to supply data_payload config.

The user and password config will then be redundant.
