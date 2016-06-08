#!/Users/pagapow/anaconda/bin/python
"""
Convert a compact REDCap data dictionary to the full and proper form.
"""

### IMPORTS

### CONSTANTS & DEFINES

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()

import csv

from simpleredcapbuilder import __version__ as version
from simpleredcapbuilder import ExpDataDictReader
from simpleredcapbuilder import ExpandDbSchema, render_template
from simpleredcapbuilder import consts
from simpleredcapbuilder import post_validate


### CODE ###

### UTILS

import pprint
pp = pprint.PrettyPrinter (indent=2)

def pprint (x):
	pp.pprint (x)


### MAIN

def parse_clargs ():
	import argparse
	aparser = argparse.ArgumentParser()

	aparser.add_argument ('infile', help='compact REDCap file to be processed')

	aparser.add_argument ('-o', "--outfile",
		help='output expanded redcap data dictionary',
		default=None,
	)

	aparser.add_argument('-i', '--include-tags', action='append',
		help='only include untagged sections or those with this tag',
	)

	aparser.add_argument('-n', '--name', action='store_true',
		help='name the output file for the tags passed in',
		default=False,
	)

#	aparser.add_argument ('-v', "--includes-vars",
#		help='include external file of variable',
#		default=None,
#	)

	args = aparser.parse_args()

	if args.outfile == None:
		if args.name and args.include_tags:
			ext = '.inc-%s.expanded.csv' % '-'.join (args.include_tags)
		else:
			ext = '.expanded.csv'
		args.outfile = args.infile.replace ('.csv', ext)

	return args


def parse_included_vars (inc_var_pth):
	ext = os.path.splitext (inc_var_pth)[1][1:].lower()
	assert ext in FMTS, "external data format '%s' not recognised"
	data = open (inc_var_pth, 'rU').read()

	if ext in ['json']:
		pass
	elif ext in ['ini']:
		pass
	elif ext in ['yml', 'yaml']:
		pass
# 
# # json - builtin json or simplejson as a fallback
# try:
#     import json
# 
#     formats['json'] = (json.loads, ValueError, MalformedJSON)
# except ImportError:
#     try:
#         import simplejson
# 
#         formats['json'] = (
#             simplejson.loads,
#             simplejson.decoder.JSONDecodeError,
#             MalformedJSON,
#         )
#     except ImportError:
#         pass
# 
# 
# # ini - Nobody likes you.
# try:
#     # Python 2
#     import ConfigParser
# except ImportError:
#     # Python 3
#     import configparser as ConfigParser
# 
# 
# def _parse_ini(data):
#     import StringIO
# 
#     class MyConfigParser(ConfigParser.ConfigParser):
#         def as_dict(self):
#             d = dict(self._sections)
#             for k in d:
#                 d[k] = dict(self._defaults, **d[k])
#                 d[k].pop('__name__', None)
#             return d
# 
#     p = MyConfigParser()
#     p.readfp(StringIO.StringIO(data))
#     return p.as_dict()
# 
# 
# formats['ini'] = (_parse_ini, ConfigParser.Error, MalformedINI)
# 
# 
# # yaml - with PyYAML
# try:
#     import yaml
# 
#     formats['yaml'] = formats['yml'] = (
#         yaml.load,
#         yaml.YAMLError,
#         MalformedYAML,
#     )
# except ImportError:
#     pass




def main ():
	args = parse_clargs()

	# read in compact dd and parse out structure
	print ("Parsing & validating input file ...")
	rdr = ExpDataDictReader (args.infile)
	exp_dd_struct = rdr.parse()

	# read in compact dd and parse out structure
	#if args.include_vars:
	#	print ("Parsing file of included variables ...")
	#	inc_vars = parse_included_vars (args.include_vars)

	# dump structure as json
	print ("Dumping structure as JSON ...")
	import json
	json_pth = args.infile.replace ('.csv', '.json')
	with open (json_pth, 'w') as out_hndl:
	    json.dump (exp_dd_struct, out_hndl, indent=3)

	# expand structure to templ
	print ("Expanding structure to template ...")
	tmpl_pth = args.infile.replace ('.csv', '.jinja')
	xpndr = ExpandDbSchema()
	xpndr.expand (exp_dd_struct, using_tags=args.include_tags, out_pth=tmpl_pth)

	# now render the template
	print ("Rendering template ...")
	with open (tmpl_pth, 'rU') as in_hndl:
		tmpl_data = in_hndl.read()
	exp_tmpl = render_template (tmpl_data, {'tags': args.include_tags})
	print ("Saving template as data dictionary ...")
	with open (args.outfile, 'w') as out_hndl:
		out_hndl.write (exp_tmpl)

	# do the postvalidation
	print ("Post-validating output data dictionary ...")
	with open (args.outfile, 'rU') as in_hndl:
		rdr = csv.DictReader (in_hndl)
		for r in rdr:
			post_validate (r)

	print ("Done.")



if __name__ == '__main__':
	import sys
	main()
	sys.exit (0)


### END ###
