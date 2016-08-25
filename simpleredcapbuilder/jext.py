"""
Jinja extensions.
"""

### IMPORTS

import re

import jinja2


### CONSTANTS & DEFINES

EXT_DICT = {}
FILTER_DICT = {}

SPACE_PATT = re.compile ('[]\s\.\-\:\/]+')
BRACKETED_PATT = re.compile (r'\([^\)]+\)')


### CODE ###

def are_any_tags_selected (local_tags, selected_tags):
	"""
	Are any of the tags for the current item found in the global set of tags?

	"""
	for lt in local_tags:
		if lt in selected_tags:
			return True
	return False

EXT_DICT['are_any_tags_selected'] = are_any_tags_selected


def delim_str_to_choices (delim_str, del_bracketed=True, cap_label=True):
	"""
	Take a comma delimited string and convert it to a REDCap vocab string.

	Params:
		See `str_list_to_choices`

	Returns:
		See `str_list_to_choices`

	This allows you define a set of choices in a single string of their labels,
	seperated by commas. It splits the strings and passes it to
	`delim_str_to_choices` to do the rest of the work. Note that of course labels
	cannot contain commas.

	"""
	# split source string
	str_list = [s.strip() for s in delim_str.split (',')]
	vocab_str = str_list_to_choices (str_list, del_bracketed=del_bracketed,
		cap_label=cap_label)

	## Return:
	return vocab_str

FILTER_DICT['delim_str_to_choices'] = delim_str_to_choices


def str_list_to_choices (str_list, del_bracketed=True, cap_label=True):
	"""
	Take a list of labels and convert it to a REDCap vocab string.

	Params:
		str_list (seq): a list of choice labels or value-label pairs
		del_bracketed (bool): strip bracketed sections from the label when making
			the value
		cap_label (bool): capitalize the first letter of the label if it isn't
			already

	Returns:
		a REDCap formatted 'choices' string

	From a list of choice 'labels' (the visible title of an item), this produces
	a consistently formatted string for a set of choices for a REDCap radio /
	dropdox / checkbox. It's definitely opinionated about how it does its job:

	- values are a lowercase, underscored version of the label
	- bracketed sections in the label are elided for the value
	- The label is capitalized (the first letter is uppercase, the rest lower)
	  unless the initial letter is already uppercase.
	- Flanking whitespace is stripped everywhere.

	Finally, you can explicitly provide a value-label pair (as a sequnec)

	"""
	## Preconditions:
	assert type (str_list) in (list, tuple), \
		"expected sequence not %s" % type (str_list)
	assert 2 <= len (str_list), "need at least two choices"

	## Main:
	# derive value string and format label
	choice_prs = []
	for lbl in str_list:
		if type (lbl) in (list, tuple):
			# given value and label already
			assert len (lbl) == 2, \
				"value-label pair does not have two elements"
			val_str = lbl[0].strip()
			lbl_str = lbl[1].strip()

		else:
			# just given the label
			# clean up label
			lbl_str = lbl.strip()

			# make value by lowercasing, stripping bracketed, converting conseq
			# spaces to underscores
			val_str = lbl_str.lower()
			if del_bracketed:
				val_str = BRACKETED_PATT.sub ('', val_str).strip()
			val_str = SPACE_PATT.sub ('_', val_str)

			# capitalize label if it doesn't start with a cap
			if cap_label and lbl_str[0].islower():
				lbl_str = lbl_str.capitalize()

		choice_prs.append ((val_str, lbl_str))

	# make vocab str
	vocab_list = ['%s, %s' % (c[0], c[1]) for c in choice_prs]
	vocab_str = jinja2.Markup (' | '.join (vocab_list))

	## Return:
	return vocab_str

FILTER_DICT['str_list_to_choices'] = str_list_to_choices


### END ###
