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

package client

import (
	"fmt"
	"bytes"
	"net"
	"strconv"
	"time"
	"html/template"

	"github.com/ragsagar/netstringer"
	"github.com/spf13/cobra"
	"github.com/ybbus/jsonrpc"
	log "github.com/sirupsen/logrus"
)

var port int
var host string

var Timeout time.Duration = 1
var htmlTemplate = `<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>Ethereum Current Block Number</title>
        <meta name="description" content="eth current block">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h2>Current Ethereum Block Number</h2>
        <p>{{ . }}</p>
    </body>
</html>`

var Url = "https://mainnet.infura.io/"

// Cmd represents the client command
var Cmd = &cobra.Command{
	Use:   "client",
	Short: "Fetch the current Ethereum block number and send it to an Eth project server.",
	Run: func(cmd *cobra.Command, args []string) {
		RunClient()
	},
}

func init() {
	Cmd.Flags().IntVar(&port, "port", 0, "Port of the Eth project server, required.")
	Cmd.Flags().StringVar(&host, "host", "", "Host of the Eth project server, required.")

}

func GetCurrentBlock() (int64, error) {
	rpcClient := jsonrpc.NewRPCClient(Url)

	log.WithFields(log.Fields{"Url": Url}).Debug("Fetching current block number from Eth")

	response, err := rpcClient.Call("eth_blockNumber")
	if err != nil {
		log.WithFields(log.Fields{"error": err.Error(), "url": Url}).Warn("While connecting to Eth")
		return 0, fmt.Errorf("connection error")
	}

	value, err := strconv.ParseInt(response.Result.(string), 0, 64)
	if err != nil {
		log.WithFields(log.Fields{"error": err.Error(), "response": response}).Warn("While parsing Eth response")
		return 0, fmt.Errorf("parse error")
	}

	log.WithFields(log.Fields{"block": value}).Debug("Received block number from Eth")

	return value, nil
}

func CreateHtml(curBlock int64) (string, error) {
	var tpl bytes.Buffer

	log.Debug("Attempting to generate HTML")

	templ := template.New("eth")

	templ_c, err := templ.Parse(htmlTemplate)
	if err != nil {
		log.WithFields(log.Fields{"error": err.Error()}).Warn("While generating HTML")
		return "", fmt.Errorf("template parse error")
	}

	templ_c.Execute(&tpl, curBlock)

	return tpl.String(), nil
}

func SendHtml(host string, port int, html string) error {
	log.WithFields(log.Fields{"host": host, "port": port}).Debug("Connecting to server")

	server := fmt.Sprintf("%s:%d", host, port)
	conn, err := net.Dial("tcp", server)
	if err != nil {
		log.WithFields(log.Fields{"host": host, "port": port, "error": err.Error()}).Warn("While connecting to server")
		return fmt.Errorf("connection error")
	}

	defer conn.Close()

	conn.SetDeadline(time.Now().Add(Timeout * time.Second))

	log.Debug("Sending data to server")

	htmlBytes := []byte(html)
	htmlBytesEncoded := netstringer.Encode(htmlBytes)
	fmt.Fprint(conn, string(htmlBytesEncoded))

	return nil
}

func RunClient() {
	var curEthBlock int64

	log.WithFields(log.Fields{"host": host, "port": port}).Debug("Starting client")

	for {
		if newEthBlock, err := GetCurrentBlock(); err == nil && newEthBlock != curEthBlock {
			log.WithFields(log.Fields{"block": newEthBlock}).Debug("New block number received, preparing to send")
			if html, err := CreateHtml(newEthBlock); err == nil {
				log.Debug("HTML generated, attempting to send")
				if SendHtml(host, port, html) == nil {
					log.Debug("New block number sent to server")
					curEthBlock = newEthBlock
				}
			}
		}
		time.Sleep(5 * time.Second)
	}
}
