#!/bin/env python
import os
import sys
import pprint
import asyncio
import websockets
import inotify.adapters
from threading import Thread


EXAMPLE_CONF = """import os

PATHS = [
    {
        'dir': 'frontend/src/',
        'files': [
            'app.js',
            'utils.js'
        ]
    },
    {
        'dir': 'static/css/',
        'files': [] # empty list means all files
    },
]"""
sys.path.insert(0, os.getcwd())
try:
    import ws_livereload_conf as conf
except:
    print('Config ws_livereload_conf.py not found.')
    f = open('ws_livereload_conf.py', 'w')
    f.write(EXAMPLE_CONF)
    f.close()
    print('Default config was created in current dir. Edit it and re-start me.')
    sys.exit(0)



BOX = {'is_reload_wanted': False}
def watcher():
    print('starting...')
    i = inotify.adapters.Inotify()
    for path in conf.PATHS:
        print('watching', path['dir'])
        i.add_watch(path['dir'])
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        #print('changed:', event)
        BOX['is_reload_wanted'] = True
        BOX['fname'] = filename

watcher_thread = Thread(target = watcher).start()

async def serve(websocket, path):
    while True:
        await asyncio.sleep(1)
        if BOX['is_reload_wanted'] == True:
            print('Reload wanted')
            msg = {'reload_wanted': BOX['fname']}
            await websocket.send(str(msg).replace("'", '"'))
            BOX['is_reload_wanted'] = False

server = websockets.serve(serve, "localhost", 8100)

asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
