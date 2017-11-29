# Eth Project Golang

> Golang client and server for fetching the current Ethereum block number and sending it via TCP to the server.

This is the Golang version of the Eth project client and server.

Read the main README first to get and idea what the client and server do.

It's compatible with Go 1.8.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Tests](#tests)
- [Deployment](#deployment)

## Features

The Golang version consist of a single CLI application with two commands: `client` and `server`. 

The `client` command starts fetching the current Ethereum block from Ethereum node using JSONRPC calls and sends it to the server which is defined using `--host` and `--port` arguments. 

The `server` commands starts a TCP server on the address and port provided with the same `--host` and `--port` arguments. It also accepts additional arguments. 

 - Argument `--use-redis` tells it to use a Redis data storage for storing basic stats. Redis is used to store SHA256 hashes of received content and timestamps when they were received as well as the number of times a certain client (IP address) has sent data. Redis parameters have to be set via `--redis-host`, `--redis-port` and `--redis-db` arguments.
 - Argument `--use-mysql` tells it to use a MySQL data storage for storing received data. If used with this argument the server will create a single table (`ethereum_data`). Upon receiving data from a client the server will store the content received along with the SHA256 hash of the content. MySQL parameters have to be set via `--mysql-host`, `--mysql-user`, `--mysql-pass` and `--mysql-db` arguments.

Communication between the server and client is done with raw TCP connections. There is a small wrapper around the data sent: [`netstring`](https://en.wikipedia.org/wiki/Netstring). Since TCP is a streaming protocol, `netstring` can split the received data into individual chunks - messages.

The CLI application uses Cobra and Viper libraries for launching commands. 

The main CLI has two additional arguments.

- `--verbose` - more verbose output, prints all `log.debug` calls. Useful for testing/debugging.
- `--wait WAIT_TIME` - pauses for WAIT_TIME seconds before running the app. Useful when waiting for another service to start (i.e. MySQL in Docker-Compose)

## Setup

The Golang version is compatible with Go 1.8. It is tested on Linux and OSX.

In order to setup your environment there are a couple of steps that have to be done.

 - Initialize an empty `GOPATH` directory and create a `src` folder inside.
 - Navigate to that `src` folder.
 - Create a symbolic link to the `eth` directory inside of project directory. `ln -s ~/Workspace/eth-project/golang/eth ~/Workspace/eth-go/src/` - where the project is located at `~/Workspace/eth-project` and the GOPATH is at `~/Workspace/eth-go`
 - This step isn't absolutely necessary but it silences a couple of warnings when downloading the dependencies. These warnings are present because of the imports mentioned previously. It would be more correct to move the entire `eth` folder to the `src` folder inside your `GOPATH` but a symlink does the same.

The easiest way to fetch dependencies and run the app is using the [`go-wrapper`](https://raw.githubusercontent.com/docker-library/golang/master/go-wrapper). If you don't have `go-wrapper` installed please install it since all the examples will be using it. 

Navigate to the `eth` folder of the project i.e. `~/Workspace/eth-project/golang/eth` and run:

`go-wrapper download`

This will install all the necessary dependencies. 
 
## Usage

There are three ways of running the app.

### From terminal

Navigate to the `eth` folder of the project i.e. `~/Workspace/eth-project/golang/eth`.

First run the server:

`go-wrapper run server --host localhost --port 9999`

You can omit the `--host` and `--port` arguments and the server will be run with defaults (localhost, 9999). You can run the server with `--use-redis` and `--use-mysql` arguments to use MySQL and Redis

`go-wrapper run server --host localhost --port 9999 --use-redis --redis-host redis --redis-port 6379 --redis-db 0 --use-mysql --mysql-host mysql --mysql-user eth_user --mysql-pass eth_password --mysql-db eth`

Make sure the database is created and the user has read/write privilege on the database.

Now you can run the client:

`go-wrapper run client --host localhost --port 8888`

And that is it. The client and server will start to communicate. If you want to see more info about what happens in the apps, use the `--verbose` flag before the `client`/`server` command.

### Using Docker

The accompanying `Dockerfile` is used for building a Docker image which will start both the client and server.

Navigate to this directory and run:

`docker build -t eth-golang .`

Now run a container using:

`docker run eth-golang `

This Docker image can also be used to run only one of the parts of the system (this is used by Docker-Compose). For instance, if you want to run only a server inside of a Docker container you can do something like this:

`docker run -p 8888:8888 eth-golang eth server --host 0.0.0.0 --port 8888`

### Using Docker Compose

This is probably the easiest way to run everything together. It runs the client and server along with MySQL and Redis data storage backends.

It is advisable to spin up the data storage parts using:

`docker compose up mysql redis`

and then Ctrl-C to stop them. Spining up MySQL takes a while and the server might start before MySQL is ready. By using this we make sure that MySQL is ready. A better way would be to run a script inside the server container which waits until MySQL is ready before starting the server.

Now you can start everything together:

`docker-compose up mysql redis server client`

You can check the port mappings of MySQL and Redis by running `docker ps`. You can use the ports to connect to them (if you want to run the `stats` API or just check the databases for data).

## Tests

Tests are written using the standard Golang test framework.

Navigate to the `eth` folder of the project i.e. `~/Workspace/eth-project/golang/eth` and run `go test ./...`.

### Using Docker Compose

There's an easier way to run tests using Docker Compose. As you did for running the app, navigate to the folder and then run

`docker-compose up test`

This will run the tests in Docker. Just make sure to rebuild it with docker-compose build test if you change something.

## Deployment

Check the main README to get a better idea how to run everything in AWS.

There's a `Dockerfile-client-ecs` for running the client in AWS Elastic Container Service and a `Dockerfile-server-beanstalk` for running the server in AWS Elastic Beanstalk.
