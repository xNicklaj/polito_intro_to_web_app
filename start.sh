#!/bin/sh
pip3 install -r requirements.txt;
export FLASK_APP=app/__init__.py && flask run --host=0.0.0.0