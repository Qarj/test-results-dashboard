#!/usr/bin/env python3

version="0.1.0"

import urllib.request, os

os.system('python3 linux_delete_dashboard_then_create_empty.py')
os.system('python3 linux_start.py')
os.system('python3 load_test_data.py')
