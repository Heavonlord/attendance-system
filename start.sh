#!/bin/sh
python3 init_db.py
exec gunicorn run:app
