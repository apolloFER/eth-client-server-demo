#!/usr/bin/env bash

exec go-wrapper run server --host localhost --port 8888 &
sleep 1
exec go-wrapper run client --host localhost --port 8888