#!/bin/bash

export PGHOST=localhost
parse-server --appId APPLICATION_ID --masterKey MASTER_KEY --databaseURI postgres://localhost:5432
