import setuptools


setuptools.setup(
    install_requires=['websockets', 'asyncio', 'inotify'],
    scripts=[
        'ws_livereload/ws_livereload.py',
    ],
)
