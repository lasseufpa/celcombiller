#! /bin/bash

virtualenv -p /usr/bin/python2.7 venv
source venv/bin/activate
pip install --allow-external --allow-unverified -r requirements.txt

python adduser.py

