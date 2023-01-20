#!/bin/bash -x
if ! [[ -d venv ]] 
then
    python -m venv venv
fi
source venv/bin/activate
export FLASK_APP=app/__init__.py
pip3 install -r requirements.txt
python ./setup.py
flask run --host=0.0.0.0