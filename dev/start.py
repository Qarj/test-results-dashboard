#!/usr/bin/env python3

version="0.1.0"

import urllib.request, os, os.path,time
dir_path = os.path.dirname(os.path.realpath(__file__))

def start_server():
    if (server_is_running()):
        #print ("Server was already started")
        return

    if os.name == 'nt':
        os.system(f'start "Test Results Dashboard server" /I python ../dash/manage.py runserver {port}')
    else:
        os.system('gnome-terminal --title "Test Results Dashboard" -x bash -c "python ' + dir_path +'/../dash/manage.py runserver {port}"')
   
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
        urllib.request.urlopen(f'http://{host_name}:{port}{path}').read()
    except ConnectionRefusedError:
        #print('Connection Refused')
        return False
    except urllib.error.URLError:
        #print('URL Error')
        return False
    return True

host_name = "127.0.0.1"
port = "8811"
path = "/results"

start_server()

if (server_is_running()):
    print (f'Test Results Dashboard is running at http://{host_name}:{port}{path}')
