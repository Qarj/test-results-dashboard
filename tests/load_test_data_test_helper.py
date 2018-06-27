#!/usr/bin/env python3

version="0.1.0"

import urllib.request, os

os.system('python start.py')
os.system('python load_test_data.py')
os.system('TASKKILL /F /T /FI "WINDOWTITLE eq Test Results Dashboard server"')
