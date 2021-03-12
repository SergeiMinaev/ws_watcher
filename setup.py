import setuptools


setuptools.setup(
    install_requires=['websockets', 'asyncio', 'inotify'],
    scripts=[
        'ws_watcher/ws_watcher.py',
    ],
)
