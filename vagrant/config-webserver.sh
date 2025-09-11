#!/bin/bash

cd /home/vagrant/Plantractor/web
apt-get install -y python3 python3-pip
if [ -f /home/vagrant/Plantractor/web/requirements.txt ]; then
    pip3 install -r /home/vagrant/Plantractor/web/requirements.txt
fi
python3 main.py
