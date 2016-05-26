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
		help='output exapnded redcap data dictionary',
		default=None,
	)

	args = aparser.parse_args()

	if args.outfile == None:
		args.outfile = args.infile.replace ('.csv', '.expanded.csv')

	return args


def main ():
	args = parse_clargs()

	# read in compact dd and parse out structure
	rdr = ExpDataDictReader (args.infile)
	exp_dd_struct = rdr.parse()

	# dump structure as json
	import json
	json_pth = args.infile.replace ('.csv', '.json')
	with open (json_pth, 'w') as out_hndl:
	    json.dump (exp_dd_struct, out_hndl, indent=3)

	# expand structure to templ
	tmpl_pth = args.infile.replace ('.csv', '.jinja')
	xpndr = ExpandDbSchema()
	xpndr.expand (exp_dd_struct, out_pth=tmpl_pth)

	# now render the template
	with open (tmpl_pth, 'rU') as in_hndl:
		tmpl_data = in_hndl.read()
	exp_tmpl = render_template (tmpl_data)
	with open (args.outfile, 'w') as out_hndl:
		out_hndl.write (exp_tmpl)

	# do the postvalidation
	with open (args.outfile, 'rU') as in_hndl:
		rdr = csv.DictReader (in_hndl)
		for r in rdr:
			post_validate (r)



if __name__ == '__main__':
	import sys
	main()
	sys.exit (0)


### END ###
