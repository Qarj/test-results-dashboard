#!/usr/bin/env python3

version="0.1.0"

import urllib.request, os, os.path, time
dir_path = os.path.dirname(os.path.realpath(__file__))

def start_server():
    if (server_is_running()):
        #print ("Server was already started")
        return

    os.system('gnome-terminal --title "Test Results Dashboard" -x bash -c "python3 ' + dir_path +'/dash/manage.py runserver"')
    
    attempts = 1
    max_attempts = 5
    while (True):
        if (server_is_running()):
            #print ("Server is now started")
            return
        attempts += 1
        if (attempts > max_attempts):
            raise RuntimeError('Server did not start')
        time.sleep(1)

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
    os.system('python3 delete_dashboard_then_create_empty.py')

start_server()

if (server_is_running()):
    print ("Test Results Dashboard is running at http://" + host_name + port + path)
