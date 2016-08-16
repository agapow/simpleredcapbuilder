"""
Jinja extensions.
"""

### IMPORTS

import re


### CONSTANTS & DEFINES

EXT_DICT = {}
FILTER_DICT = {}

SPACE_PATT = re.compile ('[]\s\.\-\:\/]+')


### CODE ###

def are_any_tags_selected (local_tags, selected_tags):
	for lt in local_tags:
		if lt in selected_tags:
			return True
	return False

EXT_DICT['are_any_tags_selected'] = are_any_tags_selected


def delim_str_to_choices (delim_str):
	"""
	Take a comma delimited string and convert it to a REDCap vocab string.

	Note the values cannot contain commas as that separates choices.
	"""
	# split source string
	str_list = [s.strip() for s in delim_str.split (',')]

	## Return:
	return str_list_to_choices (str_list)

FILTER_DICT['delim_str_to_choices'] = delim_str_to_choices


def str_list_to_choices (str_list):
	"""
	Take a list of strings and convert it to a REDCap vocab string.

	"""

	# derive value string and format label
	choice_prs = []
	for lbl in str_list:
		val_str = vc_label.lower()
		val_str = SPACE_PATT.sub ('_', val_str)
		if lbl[0].islower():
			lbl = lbl.capitalize()
		choice_prs.append ((val_str, lbl))

	# make vocab str
	vocab_list = ['%s, %s' % (c[0], c[1]) for c in choice_prs]
	vocab_str = ' | '.join (vocab_list)

	## Return:
	return vocab_str

FILTER_DICT['str_list_to_choices'] = str_list_to_choices


### END ###
