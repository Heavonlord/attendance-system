echo "START SCRIPT EXECUTED"
python3 init_db.py
exec gunicorn run:app#!/bin/sh
python3 init_db.py
exec gunicorn run:app
