"#" Catalystone Rest
[![Build Status](https://travis-ci.org/sesam-community/catalystone-rest.svg?branch=master)](https://travis-ci.org/sesam-community/catalystone-rest)

A microservice to connect to catalystones REST interface for REST versions 2 and 3. Both api versions can be used with this microservice, but read through the examples on how to set them up.

It gives the options of having connections to several different endpoints, catalystone have different tokens and secrets for each of them so specify this in ENV-vars and secrets


## Environment variables

`client_id_org` - The client ID for loading organization entities into Sesam. This is only applicable in REST version 2 at the moment as REST version 3 does not support organization data.

`client_secret_org` - The client secret associated with `client_id_org`.

`client_id_user` - The client ID for loading user data into Sesan. This is supported by both REST version 2 and 3. 

`client_secret_user` - The client secret associated with client_id_user.

`get_url` - The root API URL address associated with REST version 2. This is the same for both organizations and users.

`employee_url` - The root API URL address associated with REST version 3.   

`grant_type` - The grant type for API calls.

`token_url` - The URL for acquiring an access token for the different REST versions

`api_version` - The version of the REST required. Default is 'v2'. 

## Example system configuration for v2:


```
{
  "_id": "catalystone-rest-v2",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "client_id_org": "$ENV(catalystone-v2-client_id_org)",
      "client_id_user": "$ENV(catalystone-v2-client_id_user)",
      "client_secret_org": "$SECRET(catalystone-v2-client_secret_org)",
      "client_secret_user": "$SECRET(catalystone-v2-client_secret_user)",
      "get_url": "https://bt.catalystone.com/bouvet/api/v2/export",
      "grant_type": "client_credentials",
      "token_url": "https://bt.catalystone.com/bouvet/api/v2/oauth2/token"
    },
    "image": "sesamcommunity/catalystone-rest:2.0.0",
    "port": 5000
  }
}


```

## Example pipe configuration for v2:
# This pipe loads users into Sesam:

```
{
  "_id": "catalystone-user",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "catalystone-rest-v2",
    "url": "user"
  },
  "sink": {
    "type": "dataset",
    "dataset": "catalystone-user"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "_id",
          ["string", "_S.STANDARD_FIELDS.UNIQUE_IMPORT_ID.value"]
        ],
        ["copy", "*"]
      ]
    }
  }
}


```
# This pipe loads organisations into Sesam:
```

{
  "_id": "catalystone-organization",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "catalystone-rest-v2",
    "url": "organization"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}

```


## Example system configuration for v3:


```
{
  "_id": "catalystone-rest-v3",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "api_version": "v3",
      "client_id_user": "$ENV(catalystone-v3-client_id_user)",
      "client_secret_user": "$SECRET(catalystone-v3-client_secret_user)",
      "employee_url": "https://bt.catalystone.com/bouvet/api/employees",
      "grant_type": "client_credentials",
      "token_url": "https://bt.catalystone.com/bouvet/api/accesstoken"
    },
    "image": "sesamcommunity/catalystone-rest:2.0.0",
    "port": 5000
  }
}


```

## Example pipe configurations for v3:
# This pipe loads users into Sesam:

```

{
  "_id": "catalystone-user",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "catalystone-rest-v3",
    "url": "employees"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "_id", "_S.employeeId"],
        ["copy", "*"]
      ]
    }
  }
}

```

# This pipe creates the payloads for field numbers 101 and 7 to post to users for v3:

```
{
  "_id": "user-catalystone",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "global-person"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "employees",
          ["list",
            ["dict", "guid", "_S.guid", "field",
              ["dict", "101",
                ["dict", "data",
                  ["dict", "value",
                    ["first", "<some value>"]
                  ]
                ], "7",
                ["dict", "data",
                  ["dict", "value",
                    ["first", "<some value>"]
                  ]
                ]
              ]
            ]
          ]
        ]
      ]
    }
  }
}

```


# This pipe posts users for v3:

```
{
  "_id": "user-catalystone-endpoint",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "user-catalystone"
  },
  "sink": {
    "type": "json",
    "system": "catalystone-rest-v3",
    "url": "/post_employees"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["filter",
          ["eq", "_S._deleted", false]
        ],
        ["copy", "*"],
        ["remove", "_*"]
      ]
    }
  }
}


```

The catalystone-user pipe for version 3 can also utilize queries when loading user data. To specify a query, put "employees;<query>" in the url tag in the pipe config. To see what queries are available, please read the catalystone version 3.0 API documentation. 
