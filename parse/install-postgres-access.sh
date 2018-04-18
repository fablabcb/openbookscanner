#!/bin/bash

# from https://stackoverflow.com/a/7526119
sudo sed -i s/md5/trust/g /etc/postgresql/9.6/main/pg_hba.conf
sudo sed -i s/peer/trust/g /etc/postgresql/9.6/main/pg_hba.conf
sudo service postgresql reload
sudo -u postgres createuser "$USER"
sudo -u postgres createdb "$USER"

