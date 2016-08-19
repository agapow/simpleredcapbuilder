"""
Read external variables from a file.
"""

### IMPORTS

import os

from .utils import pprint

__all__ = [
	'ext_from_path',
	'ext_to_format',
	'parse_ext_vars',
]


### CONSTANTS & DEFINES

### CODE ###

def ext_from_path (pth):
	return os.path.splitext (pth)[1][1:]


def ext_to_format (ext):
	fmt_map = {
		'JSON': 'JSON',
		'YML': 'YAML',
		'YAML': 'YAML',
		'INI': 'INI',
		'CFG': 'INI',
		'CONFIG': 'INI',
	}
	fmt = fmt_map.get (ext.upper(), None)
	if fmt:
		return fmt
	else:
		raise ValueError ("unrecognised file format '%s'" % ext)


def parse_ext_vars (data, fmt):
	if fmt == 'JSON':
		import json
		try:
			vars = json.loads (data)
		except ValueError as err:
			raise ValueError ("malformed JSON '%s' ..." % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	elif fmt == 'INI':
		try:
			# Python 2
			import ConfigParser
			import StringIO as io
		except ImportError:
			# Python 3
			import configparser as ConfigParser
			import io

		try:
			rdr = ConfigParser.ConfigParser()
			rdr.readfp (io.StringIO (data))
			vars = rdr._sections
		except ConfigParser.Error as err:
			raise ValueError ("malformed INI '%s' ..." % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	elif fmt == 'YAML':
		import yaml
		try:
			vars = yaml.load (data)
		except yaml.YAMLError as err:
			raise ValueError ("malformed YAML '%s' ..." % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	else:
		raise ValueError ("unrecognised file format '%s'" % ext)

	return vars



### END ###
