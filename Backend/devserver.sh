#!/bin/sh
pip install -r requirements.txt
source .venv/bin/activate
python -m flask --app main run --debug
