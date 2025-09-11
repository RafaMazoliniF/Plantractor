#!/bin/bash

cd /home/vagrant/Plantractor/database
apt-get install -y python3 python3-pip
if [ -f /home/vagrant/Plantractor/web/requirements.txt ]; then
    pip3 install -r /home/vagrant/Plantractor/database/requirements.txt
fi
python3 api.py
