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

import re

from .consts import Column as COL
from .utils import warn, error

__all__ = [
   'pre_validate',
   'PostValidator',
]


### CONSTANTS & DEFINES

BL_STR_VAR_REGEX = re.compile (r'\[([^\]\(]+)')


### CODE ###

def complain (rec, msg):
	print ("WARNING: Record %s is possibly invalid: %s" % (
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
		if rec[COL.text_validation_type.value].strip():
			complain (rec, "radio / checkbox / dropdown has text validation")
		if rec[COL.text_validation_min.value].strip():
			complain (rec, "radio / checkbox / dropdown has text min")
		if rec[COL.text_validation_max.value].strip():
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
		if 'time' not in rec[COL.text_validation_type.value]:
			complain (rec, "looks like time but has no date validator")


def check_choices (rec):
	choices = rec[COL.choices_calculations.value].strip()
	if choices and '|' in choices and ',' in choices:
		if rec[COL.field_type.value] in ('radio', 'checkbox', 'dropdown'):
			choice_pairs = [x.strip() for x in choices.split('|')]
			if (8 < len (choice_pairs)) and (rec[COL.field_type.value] == 'radio'):
				complain (rec, 'radio with many choice should probably be dropdown')
			for cp in choice_pairs:
				if ',' not in cp:
					complain (rec, "malformed choice string '%s'" % cp)


def check_field_val (rec, col, allowed_vals):
   val = rec[col.value]
   if val not in allowed_vals:
      complain (rec, "unrecognised value '%s' for field '%s'" % (val,
         col.value))


class PostValidator (object):
   def __init__ (self):
      self.field_ids = []

   def check (self, recs):
      for r in recs:
         self.check_rec (r)

   def check_rec (self, rec):
      # check id right length
      check_id_length (rec)

      # check various fields have correct values
      check_field_val (consts.Column.field_type, consts.ALLOWED_FTYPE_VALS)
      check_field_val (consts.Column.text_validation_type,
         consts.ALLOWED_VALIDATION_VALS)
      check_field_val (consts.Column.identifier, consts.ALLOWED_IDENTIFIER_VALS)
      check_field_val (consts.Column.required_field,
         consts.ALLOWED_REQUIRED_VALS)

      # check bl vars are proper
      var_name = rec[COL.variable.value]
      if var_name in self.field_ids:
         error ("variable '%s' duplicated" % var_name)
      else:
         self.field_ids.append (rec[COL.variable.value])

      # check bl vars are proper
      bl_str = rec[COL.branching_logic.value]
      var_names = [m for m in BL_STR_VAR_REGEX.finditer (bl_str)]
      for m in var_names:
         curr_var = m.groups()[0]
         if curr_var not in self.field_ids:
            complain (rec, "unrecognised variable '%s' in branching logic" % curr_var)


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
