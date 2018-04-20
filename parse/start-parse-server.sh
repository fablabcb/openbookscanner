#!/bin/bash

cd "`dirname \"$0\"`"

export PGHOST=localhost
parse-server configuration.json
#	--appId OpenBookScanner \
#	--masterKey MASTER_KEY \
#	--databaseURI postgres://localhost:5432 \
#	--logLevel debug \
#	--startLiveQueryServer true
