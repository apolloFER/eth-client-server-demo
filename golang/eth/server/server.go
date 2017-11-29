// Copyright © 2017 NAME HERE <EMAIL ADDRESS>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package server

import (
	"fmt"
	"net"
	"strings"
	"time"

	"crypto/sha256"
	"encoding/hex"
	"github.com/jinzhu/gorm"
	"github.com/go-redis/redis"
	"github.com/ragsagar/netstringer"
	"github.com/spf13/cobra"
	log "github.com/sirupsen/logrus"
	_ "github.com/go-sql-driver/mysql"
	_ "github.com/jinzhu/gorm/dialects/mysql"
)

var useRedis bool
var useMySQL bool
var port int
var host string
var redisHost string
var redisPort int
var redisDb int
var mySQLHost string
var mySQLUser string
var mySQLPass string
var mySQLDb string

var Timeout time.Duration = 1
var RedisHashTimestampKey = "eth:hashes"
var RedisClientCountKey = "eth:ip_addresses"

type StatsData struct {
	payload  string
	clientIp string
}

var redisStoreChan = make(chan StatsData)
var mySQLStoreChan = make(chan StatsData)

// Cmd represents the server command
var Cmd = &cobra.Command{
	Use:   "server",
	Short: "Run an Eth project server for receiving Ethereum block numbers.",
	Run: func(cmd *cobra.Command, args []string) {
		RunServer()
	},
	PreRunE: func(cmd *cobra.Command, args []string) error {
		if useRedis {
			if redisHost == "" {
				return fmt.Errorf("--use-redis called without --redis-host")
			}
			if redisPort <= 0 {
				return fmt.Errorf("--use-redis called without --redis-port")
			}
			if redisDb < 0 {
				return fmt.Errorf("--use-redis called without --redis-db")
			}
		}

		if useMySQL {
			if mySQLHost == "" {
				return fmt.Errorf("--use-mysql called without --mysql-host")
			}
			if mySQLUser == "" {
				return fmt.Errorf("--use-mysql called without --mysql-user")
			}
			if mySQLPass == "" {
				return fmt.Errorf("--use-mysql called without --mysql-pass")
			}
			if mySQLDb == "" {
				return fmt.Errorf("--use-mysql called without --mysql-db")
			}
		}

		return nil
	},
}

func init() {
	Cmd.Flags().BoolVar(&useRedis, "use-redis", false, "Use Redis data storage.")
	Cmd.Flags().BoolVar(&useMySQL, "use-mysql", false, "Use MySQL data storage.")
	Cmd.Flags().StringVar(&redisHost, "redis-host", "", "Redis hostname.")
	Cmd.Flags().IntVar(&redisPort, "redis-port", 0, "Redis port.")
	Cmd.Flags().IntVar(&redisDb, "redis-db", 0, "Redis database number.")
	Cmd.Flags().StringVar(&mySQLHost, "mysql-host", "", "MySQL hostname.")
	Cmd.Flags().StringVar(&mySQLUser, "mysql-user", "", "MySQL username.")
	Cmd.Flags().StringVar(&mySQLPass, "mysql-pass", "", "MySQL password.")
	Cmd.Flags().StringVar(&mySQLDb, "mysql-db", "", "MySQL database to use.")
	Cmd.Flags().IntVar(&port, "port", 9999, "Port for the Eth server.")
	Cmd.Flags().StringVar(&host, "host", "localhost", "Host for the Eth server.")
}

func ClientProcessor(conn net.Conn) {
	defer conn.Close()

	log.WithFields(log.Fields{"client": conn.RemoteAddr().String()}).Debug("Client connected")

	decoder := netstringer.NewDecoder()

	var payload string

ReadLoop:
	for {
		buffer := make([]byte, 512)
		conn.SetDeadline(time.Now().Add(Timeout * time.Second))

		bytesRead, err := conn.Read(buffer)

		log.WithFields(log.Fields{"raw": buffer}).Debug("Raw data received")

		if err != nil || bytesRead == 0 {
			log.WithFields(log.Fields{"addr": conn.RemoteAddr().String()}).Warn("Error while receiving data")
			fmt.Printf("Error while receiving data from %v\n", conn.RemoteAddr().String())
			return
		}

		decoder.FeedData(buffer[:bytesRead])

		select {
		case data := <-decoder.DataOutput:
			payload = string(data)
			log.WithFields(log.Fields{"payload": payload}).Debug("New client message received")
			break ReadLoop
		default:
			continue
		}

	}

	fmt.Printf("DATA - %v - %s\n", conn.RemoteAddr().String(), strings.Replace(payload, "\n", "\\n", -1))

	stats := StatsData{payload: payload, clientIp: strings.Split(conn.RemoteAddr().String(), ":")[0]}

	if useRedis {
		log.Debug("Sending stats to Redis")
		redisStoreChan <- stats
	}

	if useMySQL {
		log.Debug("Sending stats to MySQL")
		mySQLStoreChan <- stats
	}
}

func RedisProcessor() {
	log.WithFields(log.Fields{"host": redisHost, "port": redisPort, "db": redisDb}).Debug("Establishing Redis connection")

	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%d", redisHost, redisPort),
		Password: "",      // no password set
		DB:       redisDb, // use default DB
	})

	ping := client.Ping()

	if ping.Err() != nil {
		log.WithFields(log.Fields{"host": redisHost, "port": redisPort, "db": redisDb}).Error("Could not connect to Redis")
		return
	}

	for value := range redisStoreChan {
		timestamp := float64(time.Now().UnixNano()) / float64(time.Second)

		hasher := sha256.New()
		hasher.Write([]byte(value.payload))
		payloadHash := hex.EncodeToString(hasher.Sum(nil))

		log.WithFields(log.Fields{"hash": payloadHash}).Debug("Payload hash calculated")

		client.ZAddNX(RedisHashTimestampKey, redis.Z{timestamp, payloadHash})
		client.HIncrBy(RedisClientCountKey, value.clientIp, 1)

		log.Debug("Stats stored to Redis")
	}
}

type EthereumData struct {
	ID      uint   `gorm:"primary_key"`
	Hash    string `gorm:"size:64"`
	Payload string `sql:"type:text"`
}

func (EthereumData) TableName() string {
	return "ethereum_data"
}

func MySQLProcessor() {
	connStr := fmt.Sprintf("%s:%s@tcp(%s:3306)/%s?charset=utf8", mySQLUser, mySQLPass, mySQLHost, mySQLDb)
	db, err := gorm.Open("mysql", connStr)
	defer db.Close()

	if err != nil {
		log.WithFields(log.Fields{"error": err.Error()}).Error("During connecting to MySQL, exiting")
		return
	}

	db.AutoMigrate(&EthereumData{})
	db.Model(&EthereumData{}).AddUniqueIndex("idx_hash", "hash")

	for value := range mySQLStoreChan {
		hasher := sha256.New()
		hasher.Write([]byte(value.payload))
		payloadHash := hex.EncodeToString(hasher.Sum(nil))

		var data EthereumData
		db.Where(EthereumData{Hash: payloadHash}).Attrs(EthereumData{Payload: value.payload}).FirstOrCreate(&data)
		if data.ID == 0 {
			log.WithFields(log.Fields{"hash": payloadHash}).Warn("Error while adding data to MySQL")
		} else {
			log.WithFields(log.Fields{"hash": payloadHash, "Id": data.ID}).Debug("Stored data to MySQL")
		}
	}
}

func RunServer() {
	log.WithFields(log.Fields{"host": host, "port": port}).Debug("Starting server")

	if useRedis {
		go RedisProcessor()
	}

	if useMySQL {
		go MySQLProcessor()
	}


	listener, err := net.Listen("tcp", fmt.Sprintf("%s:%d", host, port))

	if err != nil {
		log.WithFields(log.Fields{"error": err.Error()}).Error("During server startup, exiting")
		return
	}

	defer listener.Close()

	for {
		conn, err := listener.Accept()

		if err != nil {
			log.WithFields(log.Fields{"error": err.Error()}).Warn("During client connect")
			continue
		}

		go ClientProcessor(conn)
	}
}
