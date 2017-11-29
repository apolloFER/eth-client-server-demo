# ETH Client Server Demo Project

> ETH Client Server Demo project consists of Go and Python implementation of a TCP client/server. There's also a stats API and MySQL/Redis support. Infrastructure wise it's designed to be deployed to AWS using a number of services.

The client fetches the latest Ethereum block number from the mainnet using the Ethereum node JSONRPC backend. If the block number has changed it creates a HTML document using a predefined template and sends it to server via a new TCP connection. The server receives the HTML and prints the contents along with the client IP and port. It can also store various stats and data to MySQL and/or Redis.

There's a stats API written in Python that connects to MySQL and Redis and allows access to data received and client stats.

Currently the code is compatible with Go 1.8 and Python 3.6.

## Table of Contents

- [Features](#features)
- [Deployment](#deployment)

## Features

The features of each implementation can be seen in the README.md file of the corresponding implementation.

All versions are interoperable, meaning that Python client can communicate with Go server and vice versa. The server component has support for creating MySQL tables on startup. Tables created by each version are also interoperable. The idea is to allow instances of both Golang and Python server running in a parallel load balanced way with 1+ clients connecting to them. Which ever server receives the first block number (i.e. the same generated HTML will store it in the database backend while the later copies of the HTML will not be stored.

Both versions have similar CLI with arguments and commands being the same. Behaviour is very similar (with some small changes accounting to different properties of each language e.g. goroutines etc.)

CLIs are created using `Cobra`/`Viper` in Golang and `Click` in Python.

MySQL is accessed using `gorm` in Golang and `SQLAlchemy` in Python.

Logging has general and verbose mode and uses standard `logging` in Python and `logrus` in Golang. 

JSONRPC calls are done using `requests` in Python and `jsonrpc` library in Golang (v2 compatible).

Messages sent from client to server are packed with `netstring` which allows easier decoding (with *delimiters* between messages). This is not necessarily needed but becomes useful if/when there's a long lasting TCP connection and a number of messages sent back and forth.

Both implementations use Docker and Docker-Compose to ease the process of running and testing.

Deployment of everyhing together is more complex and is the subject of next topic.

## Deployment

The entire project is designed to be deployed to AWS. It uses a number of AWS services:

- AWS Elastic Container Service - for hosting client image repos and running clients on a ECS Cluster
- AWS Elastic Beanstalk - for running each server implementation (via Docker Beanstalk support)
- AWS RDS - a MySQL instance for data storage
- AWS Elasticache - a Redis instance for data storage
- AWS Route53 - for DNS loadbalancing between servers
- AWS Lambda, AWS API Gateway, AWS Certificate Manager, AWS Cloudfront - for deploying the stats API using Zappa

Both implementations have a `Dockerfile-client-ecs`. This is used for building a Docker image which is pushed to ECS Docker Registry. The server address is hardcoded during launch (but uses the *ronic.co* domain so it can be tuned using Route53). The clients are then run on a ECS cluster using Task definitions.

Both implementation have `Dockerfile-server-beanstalk` and `dockerrun.aws.json` files. These are used for deploying the server components to AWS Elastic Beanstalk. The URLs for MySQL and Redis are hardcoded during launch (also use the *ronic.co* domain). Each version is a separate Beanstalk application. The implementations are loadbalanced using Route53 which replies with different version URL on each DNS request.

The stats API is a strange animal in terms of AWS deployments. It uses Zappa framework which deploys this Flask web application to AWS Lambda. API Gateway endpoints and Cloudfront distributions are generated as well. This enables HTTPS support using the AWS generated SSL certificates.
