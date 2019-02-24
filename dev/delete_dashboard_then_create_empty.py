#!/usr/bin/env python3

version="0.1.0"

import os
import shutil

def remove_if_exists(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

if os.name == 'nt':
    os.system('TASKKILL /F /T /FI "WINDOWTITLE eq Test Results Dashboard server"')

remove_if_exists("../dash/db.sqlite3")
shutil.rmtree('../dash/results/migrations', ignore_errors=True)
shutil.rmtree('../dash/results/migrations', ignore_errors=True)
shutil.rmtree('../dash/results/migrations', ignore_errors=True)
shutil.rmtree('../dash/artefacts', ignore_errors=True)
shutil.rmtree('../dash/artefacts', ignore_errors=True)
shutil.rmtree('../dash/artefacts', ignore_errors=True)

os.system('python ../dash/manage.py makemigrations results')
os.system('python ../dash/manage.py migrate')
