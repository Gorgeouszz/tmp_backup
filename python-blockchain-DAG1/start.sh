#!/bin/sh
pip install -r requirements.txt
export FLASK_APP=node_server.py
flask run --port 8001
