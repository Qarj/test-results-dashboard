#!/usr/bin/env python3

version="0.1.0"

import urllib.request, os, os.path

def start_server():
    if (server_is_running()):
        #print ("Server was already started")
        return

    os.system('start "Test Results Dashboard server" /I python dash/manage.py runserver')
    
    attempts = 1
    max_attempts = 5
    while (True):
        if (server_is_running()):
            #print ("Server is now started")
            return
        attempts += 1
        if (attempts > max_attempts):
            raise RuntimeError('Server did not start')

def server_is_running():
    try:
        urllib.request.urlopen("http://" + host_name + port + path).read()
    except ConnectionRefusedError:
        #print('Connection Refused')
        return False
    except urllib.error.URLError:
        #print('URL Error')
        return False
    return True

host_name = "127.0.0.1"
port = ":8000"
path = "/results"

if (not os.path.isfile("dash/results/migrations/0001_initial.py")):
    os.system('python delete_dashboard_then_create_empty.py')

start_server()

if (server_is_running()):
    print ("Test Results Dashboard is running at http://" + host_name + port + path)
