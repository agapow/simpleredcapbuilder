"""
Some validation and checking functions for REDCap data dictionaries.
"""

### IMPORTS

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from .consts import Column as COL

__all__ = [
   'pre_validate',
   'post_validate',
]


### CONSTANTS & DEFINES

### CODE ###

def complain (rec, msg):
	print ("Record %s is possibly invalid: %s" % (
      rec[COL.variable.value],
      msg,
   ))


def check_id_length (rec):
   variable = rec[COL.variable.value]
   if 26 < len (variable):
      complain (rec, "variable identifier is too long")


def check_needs_choices (rec):
	if rec[COL.field_type.value] in ('radio', 'checkbox', 'dropdown'):
		if not rec[COL.choices_calculations.value].strip():
			complain (rec, "radio / checkbox / dropdown has no choices")
		if rec[Column.text_validation_type.value].strip():
			complain (rec, "radio / checkbox / dropdown has text validation")
		if rec[Column.text_validation_min.value].strip():
			complain (rec, "radio / checkbox / dropdown has text min")
		if rec[Column.text_validation_max.value].strip():
			complain (rec, "radio / checkbox / dropdown has text max")
	else:
		if rec[COL.text_validation_type.value] not in ('number', 'integer'):
			if rec[COL.choices_calculations.value].strip():
				complain (rec, "non-radio / checkbox / dropdown / numeric has choices or calculation")


def check_dates_and_times (rec):
	if ('date' in rec[COL.field_label.value].lower()) or ('date' in rec[COL.variable.value].lower()):
		if 'date' not in rec[COL.text_validation_type.value]:
			complain (rec, "looks like date but has no date validator")

	if ('time' in rec[COL.field_label.value].lower()) or ('time' in rec[COL.variable.value].lower()):
		if 'time' not in rec[Column.text_validation_type.value]:
			complain (rec, "looks like time but has no date validator")


def check_choices (rec):
	choices = rec[COL.choices_calculations.value].strip()
	if choices and '|' in choices and ',' in choices:
		for cp in [x.strip() for x in choices.split('|')]:
			if ',' not in cp:
				complain (rec, "malformed choice string '%s'" % cp)
			else:
				if cp.count (',') != 1:
					complain (rec, "malformed choice string '%s'" % cp)


def post_validate (rec):
   """
   Check a final record for potential problems.

   At the moment we just check the id, because it could have altered between
   the input and output. Everything else is taken care of in pre-validation.
   """
   check_id_length (rec)


def pre_validate (rec):
   """
   Check an input record for potential problems.

   It makes sense to check for most issues here because with repetition the
   'same' error could be caught multiple times. Best to look for it in the
   source.
   """
   check_id_length (rec)
   check_needs_choices (rec)
   check_dates_and_times (rec)
   check_choices (rec)


### END ###
