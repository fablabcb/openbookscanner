#!/bin/bash

sudo -u postgres dropdb "$USER"
sudo -u postgres createdb "$USER"


