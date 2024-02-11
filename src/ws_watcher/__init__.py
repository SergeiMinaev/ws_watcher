import asyncio
from ws_watcher import ws_watcher


try:
	asyncio.run(ws_watcher.main())
except KeyboardInterrupt:
	print('Stopping...')
