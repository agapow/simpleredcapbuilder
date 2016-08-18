"""
Module-wide utility functions
"""

### IMPORTS

import os
import pprint

__all__ = [
	'pprint',
	'progress',
	'warn',
	'error',
]


### CONSTANTS & DEFINES

_PP = pprint.PrettyPrinter (indent=2)


### CODE ###

def pprint (x):
	_PP.pprint (x)


def progress (msg):
	print ("%s ..." % msg)


def warn (msg):
	print ("WARNING: %s" % msg)


def error (msg):
	print ("ERROR: %s" % msg)


### END ###
