#!/usr/bin/env bash
set -o errexit

pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python -m ml.build_pipeline
python manage.py migrate