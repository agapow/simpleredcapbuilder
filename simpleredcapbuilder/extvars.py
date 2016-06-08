"""
Read external variables from a file.
"""

### IMPORTS

import os

__all__ = [
	'ext_from_path',
	'ext_to_format',
	'parse_ext_vars',
]


### CONSTANTS & DEFINES

### CODE ###

def ext_from_path (pth):
	return ext = os.path.splitext (inc_var_pth)[1][1:]


def ext_to_format (ext):
	fmt_map = {
		'JSON': 'JSON',
		'YML': 'YAML',
		'YAML': 'YAML',
		'INI': 'INI',
	}
	fmt = fmt_map.get (ext.upper(), None)
	if fmt:
		return fmt
	else:
		raise ValueError ("unrecognised file format '%s'" % ext)


def parse_ext_vars (data, fmt):
	if ext in ['json']:
		import json
		try:
			vars = json.loads (data)
		except ValueError as err:
			raise MalformedJSON (u'%s ...' % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	elif ext in ['ini']:
		try:
			# Python 2
			import ConfigParser
		except ImportError:
			# Python 3
			import configparser as ConfigParser

		try:
			rdr = ConfigParser()
			import StringIO
			rdr.readfp (StringIO.StringIO (data))
			vars = rdr.as_dict()
		except ConfigParser.Error as err:
			raise MalformedINI (u'%s ...' % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	elif ext in ['yml', 'yaml']:
		import yaml
		try:
			vars = yaml.load (data)
		except yaml.YAMLError as err:
			raise MalformedJSON (u'%s ...' % data[:40])
		except ImportError:
			raise RuntimeError ('no library for handling JSON-formatted data')

	else:
		raise ValueError ("unrecognised file format '%s'" % ext)

	return vars



### END ###
