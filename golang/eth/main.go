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

package main

import (
	log "github.com/sirupsen/logrus"
	"github.com/mitchellh/go-homedir"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"eth/client"
	"eth/server"
	"os"
	"time"
)

var cfgFile string
var verbose bool
var wait int

// RootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "eth",
	Short: "Eth project client and server implementation in Go.",
	Long: `Go implementation of a client and server that communicate via TCP connections.

Compatible with the Python version of client and server.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	//	Run: func(cmd *cobra.Command, args []string) { },
}

func init() {
	cobra.OnInitialize(initLog)
	cobra.OnInitialize(initConfig)
	cobra.OnInitialize(checkWait)
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "Verbose logging.")
	rootCmd.PersistentFlags().IntVar(&wait, "wait", 0, "Wait before starting.")
}

// initConfig reads in config file and ENV variables if set.
func initConfig() {
	if cfgFile != "" {
		// Use config file from the flag.
		viper.SetConfigFile(cfgFile)
	} else {
		// Find home directory.
		home, err := homedir.Dir()
		if err != nil {
			log.Error(err)
			os.Exit(1)
		}

		// Search config in home directory with name ".eth" (without extension).
		viper.AddConfigPath(home)
		viper.SetConfigName(".eth")
	}

	viper.AutomaticEnv() // read in environment variables that match
	viper.SetEnvPrefix("eth")

	// If a config file is found, read it in.
	if err := viper.ReadInConfig(); err == nil {
		log.WithFields(log.Fields{"file": viper.ConfigFileUsed()}).Debug("Using config file")
	}
}

func initLog() {
	if verbose {
		log.SetLevel(log.DebugLevel)
	} else {
		log.SetLevel(log.WarnLevel)
	}
}

func checkWait() {
	if wait > 0 {
		time.Sleep(time.Duration(wait) * time.Second)
	}
}

func main() {
	addCommands()

	if err := rootCmd.Execute(); err != nil {
		log.Error(err)
		os.Exit(1)
	}
}

//AddCommands adds child commands to the root command rootCmd.
func addCommands() {
	rootCmd.AddCommand(server.Cmd)
	rootCmd.AddCommand(client.Cmd)
}
