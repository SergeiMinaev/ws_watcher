import os
from os.path import join


BASE_DIR = os.environ['MYPROJECT_HOME']


PATHS = [
    {
        'dir': join(BASE_DIR, 'relative/path/to/js'),
    },
    {
        'dir': '/absolute/path/to/styles'),
		'onchange': {
			'cmds': [
				'build_css.sh',
			],
		},
    },
]
