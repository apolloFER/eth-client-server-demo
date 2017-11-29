package server

import (
    "testing"
)


func TestWrongServer(t *testing.T) {
	host = "aaaaaa"
	port = 2000
	RunServer()
}

func TestWrongRedis(t *testing.T) {
	redisHost = "aaaaaa"
	redisPort = 10101
	redisDb = 17
	close(redisStoreChan)
	RedisProcessor()
}

func TestWrongMySQL(t *testing.T) {
	mySQLHost = "aaaaaa"
	mySQLUser = "aaaaaa"
	mySQLPass = "aaaaaa"
	mySQLDb = "aaaaaa"
	close(mySQLStoreChan)
	MySQLProcessor()
}
