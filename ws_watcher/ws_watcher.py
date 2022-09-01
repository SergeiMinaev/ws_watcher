#!/bin/env python
import os
import sys
import pprint
import asyncio
import signal
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
                BOX['is_send_ws_msg'] = q.get('onchange', {}).get('is_send_ws_msg', True)
                BOX['fname'] = filename
                for cmd in q.get('onchange', {}).get('cmds', [])
                    print(f'executing {cmd}...')
                    subprocess.Popen([cmd], shell=True)

watcher_thread = Thread(target=watcher, daemon=True).start()

async def handler(websocket):
    while True:
        await asyncio.sleep(0.3)
        if BOX['is_send_ws_msg'] == True:
            #print('Reload wanted', BOX['fname'])
            msg = {'reload_wanted': BOX['fname']}
            await websocket.ping()
            await websocket.send(str(msg).replace("'", '"'))
            BOX['is_send_ws_msg'] = False
            BOX['fname'] = None

async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    async with websockets.serve(handler, "localhost", 8100):
        await stop

asyncio.run(main())
