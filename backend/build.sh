#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python -m ml.build_pipeline
python manage.py migrate
python manage.py collectstatic --no-input