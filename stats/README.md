# Eth Project Stats

> Simple cat like API, inspired by Elasticsearch's *_cat* API. Shows stats of the running server.

Read the main README first to get and idea what the stats part does.

It's compatible with Python 3.6.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Deployment](#deployment)

## Features

This is the stats API for the server/client (both Go and Python versions are supported). It is inspired by Elasticsearch's *_cat* API. It's done with `Flask` and `tabulate`.

The root URI is `/_cat` which will display all possible API calls.

The API calls are:

 - `/_cat/hashes` - displays last 100 hashes of content received from clients and the timestamps when they were received
 - `/_cat/hashes/{hash}` - displays the content received (by hash)
 - `/_cat/clients` - displays the stats of clients, how many messages were received by a client

The stats API needs values for MySQL and Redis databases. It fetches them from environment variables:
 
 - `REDIS_HOST`
 - `REDIS_PORT`
 - `REDIS_DB`
 - `MYSQL_HOST`
 - `MYSQL_PORT`
 - `MYSQL_USER`
 - `MYSQL_PASS`
 - `MYSQL_DB`

There are some default values for those arguments which can be checked in the `stats.py` file.
 
## Setup

The stats API is compatible with Python 3.6 (and probably 3.5). It is tested on Linux and OSX.

It's advisable to use virtualenv.

Requirements for running the app are in the ```requirements.txt``` file. Install them (in a virtualenv) using

```pip install -r requirements.txt```

## Usage

Navigate to the folder where stats API resides and activate your preconfigured virtualenv.

Setup all environment variables. If you launched the client/server using Docker Compose now it's time to check out the mapped ports of Redis and MySQL and use them for stats API along with `localhost` for hostname. MySQL user/pass/database can be checked in the corresponding docker-compose.yml of the project.

Run in using `FLASK_APP=stats.py flask run` and navigate to `http://localhost:5000/` in your browser.

## Deployment

Check the main README to get a better idea how to run everything in AWS.

The stats API uses Zappa for deployment. Zappa allows you to deploy your Flask/Django/... web app to AWS Lambda and generates the proper AWS API Gateway endpoints for accessing it. It can also setup DNS using Route53 and SSL certificates from AWS Cerificate Manager.

There's a `zappa_settings.json` for deploying stats API to AWS Lambda. You can read more about Zappa [here](https://github.com/Miserlou/Zappa).
