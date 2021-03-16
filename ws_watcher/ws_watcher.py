#!/bin/env python
import os
import sys
import pprint
import asyncio
import websockets
import subprocess
import inotify.adapters
from threading import Thread


EXAMPLE_CONF = """import os

SETUP = [
    {
        'dir': 'frontend/src/',
        'files': [
            'app.js',
            'utils.js'
        ],
        'onchange': {
            'is_send_ws_msg': True,
            'cmds': [
                'echo "Hello!"',
            ]
        },
    },
    {
        'dir': 'static/css/',
        'files': [] # empty list means all files
    },
]"""
sys.path.insert(0, os.getcwd())
try:
    import conf_ws_watcher as conf
except:
    print('Config conf_ws_watcher.py not found.')
    f = open('conf_ws_watcher.py', 'w')
    f.write(EXAMPLE_CONF)
    f.close()
    print('Default config was created in current dir. Edit it and re-start me.')
    sys.exit(0)



BOX = {'is_send_ws_msg': False}
def watcher():
    print('starting...')
    i = inotify.adapters.Inotify()
    for path in conf.SETUP:
        print('watching', path['dir'])
        i.add_watch(path['dir'])
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        if 'IN_CLOSE_WRITE' in type_names:
            print('changed:', path, filename)
            for q in filter(lambda q: q['dir'] == path, conf.SETUP):
                BOX['is_send_ws_msg'] = q['onchange']['is_send_ws_msg']
                BOX['fname'] = filename
                for cmd in q['onchange']['cmds']:
                    print(f'executing {cmd}...')
                    subprocess.Popen([cmd], shell=True)

watcher_thread = Thread(target = watcher).start()

async def serve(websocket, path):
    while True:
        await asyncio.sleep(0.3)
        if BOX['is_send_ws_msg'] == True:
            #print('Reload wanted', BOX['fname'])
            msg = {'reload_wanted': BOX['fname']}
            await websocket.ping()
            await websocket.send(str(msg).replace("'", '"'))
            BOX['is_send_ws_msg'] = False
            BOX['fname'] = None

server = websockets.serve(serve, "localhost", 8100)

asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
