#!/usr/bin/env python3

version="0.1.0"

import os

def remove_if_exists(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

os.system('TASKKILL /F /T /FI "WINDOWTITLE eq Test Results Dashboard server"')

remove_if_exists("dash/db.sqlite3")
remove_if_exists("dash/results/migrations/0001_initial.py")
remove_if_exists("dash/polls/migrations/0001_initial.py")

os.system('python dash/manage.py makemigrations results')
os.system('python dash/manage.py makemigrations polls')
os.system('python dash/manage.py migrate')
