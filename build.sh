#! /bin/bash

virtualenv -p $(which python3) venv
source venv/bin/activate
pip install --allow-external --allow-unverified -r requirements.txt

python adduser.py

