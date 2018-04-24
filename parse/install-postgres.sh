#!/bin/bash

sudo apt-get -y install pidentd
sudo bash -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ wheezy-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgres-9.6
