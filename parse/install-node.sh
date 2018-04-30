#!/bin/bash

# from https://raspberrypi.stackexchange.com/a/37976

cd /opt

version="v9.9.0"
sudo wget https://nodejs.org/dist/$version/node-$version-linux-armv6l.tar.gz
sudo tar -xzf node-$version-linux-armv6l.tar.gz
sudo mv node-$version-linux-armv6l nodejs
sudo rm node-$version-linux-armv6l.tar.gz
sudo ln -s /opt/nodejs/bin/node /usr/bin/node
sudo ln -s /opt/nodejs/bin/npm /usr/bin/npm
