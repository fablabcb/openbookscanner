#!/bin/bash

# from https://docs.npmjs.com/getting-started/fixing-npm-permissions#option-two-change-npms-default-directory

mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.profile


