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


try:
	sys.path.insert(0, os.getcwd())
	import ws_watcher_conf as conf
	PATHS = conf.PATHS
except ModuleNotFoundError:
	BASE_DIR = os.getcwd()
	print(f'Config file ws_watcher_conf.py not found. Watching current dir: {BASE_DIR} .')
	PATHS = [
		{'dir': BASE_DIR }
	]
except Exception as e:
	print('Failed to load config:', e)


BOX = {'is_send_ws_msg': False}
def watcher():
	print('starting...')
	paths = []
	for path in PATHS:
		print('watching', path['dir'])
		if not os.path.isdir(path['dir']):
			print(f'Skipping: {path["dir"]} does not exists or not a directory.')
		else:
			paths.append(path['dir'])
	i = inotify.adapters.InotifyTrees(paths)
	for event in i.event_gen(yield_nones=False):
		(_, type_names, changed_path, filename) = event
		if 'IN_CLOSE_WRITE' in type_names:
			print('changed:', changed_path, filename)
			for q in filter(lambda q: q['dir'] in changed_path, PATHS):
				BOX['is_send_ws_msg'] = q.get('onchange', {}).get('is_send_ws_msg', True)
				BOX['fname'] = filename
				for cmd in q.get('onchange', {}).get('cmds', []):
					print(f'executing {cmd}...')
					subprocess.Popen([cmd], shell=True)

watcher_thread = Thread(target=watcher, daemon=True).start()

async def handler(websocket):
	while True:
		await asyncio.sleep(0.3)
		if BOX['is_send_ws_msg'] == True:
			msg = {'reload_wanted': BOX['fname']}
			try:
				await websocket.send(str(msg).replace("'", '"'))
			except Exception as e:
				print('Unable to send - the client is offline.')
			BOX['is_send_ws_msg'] = False
			BOX['fname'] = None


async def main():
	async with websockets.serve(handler, "localhost", 8100):
		await asyncio.Future()
