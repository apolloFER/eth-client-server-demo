#!/usr/bin/env bash

exec eth server --host localhost --port 8888 &
sleep 1
exec eth client --host localhost --port 8888