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
from . import utils

__all__ = [
	'PreValidator',
	'PostValidator',
]


### CONSTANTS & DEFINES

BL_STR_VAR_REGEX = re.compile (r'\[([^\]\(]+)')


### CODE ###

### FXNS

## Messaging

def warn_rec (rec, msg):
	"""
	Warn that a record may have problems.

	"""
	# TODO: update some warns to errors as appropriate
	msg = "Record %s is possibly invalid: %s" % (rec[COL.variable.value], msg)
	utils.warn (msg)


def error_rec (rec, msg):
	"""
	Complain that a record definitely has problems.

	"""
	msg = "Record %s is invalid: %s" % (rec[COL.variable.value], msg)
	utils.error (msg)


## Error checking

def check_id_length (rec):
	variable = rec[COL.variable.value]
	if 26 < len (variable):
		error_rec (rec, "variable identifier is too long")


def check_required_fields (rec)
	for col in consts.MANDATORY_COLS:
		col_name = col.value
		if not rec[col_name].strip():
			error_rec (rec, "missing required field '%s'" % col_name)


def check_needs_choices (rec):
	"""
	If this is a field that needs choices, see that it has them.

	"""
	if rec[COL.field_type.value] in ('radio', 'checkbox', 'dropdown'):
		if not rec[COL.choices_calculations.value].strip():
			warn_rec (rec, "radio / checkbox / dropdown has no choices")
		if rec[COL.text_validation_type.value].strip():
			warn_rec (rec, "radio / checkbox / dropdown has text validation")
		if rec[COL.text_validation_min.value].strip():
			warn_rec (rec, "radio / checkbox / dropdown has text min")
		if rec[COL.text_validation_max.value].strip():
			warn_rec (rec, "radio / checkbox / dropdown has text max")
	else:
		if rec[COL.text_validation_type.value] not in ('number', 'integer'):
			if rec[COL.choices_calculations.value].strip():
				warn_rec (rec, "non-radio / checkbox / dropdown / numeric has choices or calculation")


def check_dates_and_times (rec):
	"""
	If a record looks like a date or time, check it has right validator.

	"""
	# TODO: allow for other date and time format validators
	if ('date' in rec[COL.field_label.value].lower()) or ('date' in rec[COL.variable.value].lower()):
		if 'date' not in rec[COL.text_validation_type.value]:
			warn_rec (rec, "looks like date but has no date validator")

	if ('time' in rec[COL.field_label.value].lower()) or ('time' in rec[COL.variable.value].lower()):
		if 'time' not in rec[COL.text_validation_type.value]:
			warn_rec (rec, "looks like time but has no date validator")


def check_choices (rec):
	"""
	If this field requires a choices, does choices look valid?

	"""
	# TODO: needs honing
	choices = rec[COL.choices_calculations.value].strip()
	if choices and '|' in choices and ',' in choices:
		if rec[COL.field_type.value] in ('radio', 'checkbox', 'dropdown'):
			choice_pairs = [x.strip() for x in choices.split('|')]
			if (8 < len (choice_pairs)) and (rec[COL.field_type.value] == 'radio'):
				warn_rec (rec, 'radio with many choice should probably be dropdown')
			for cp in choice_pairs:
				if ',' not in cp:
					warn_rec (rec, "malformed choice string '%s'" % cp)


def check_field_val (rec, col, allowed_vals):
	"""
	Check that a record's val in a given column falls in a set of legal values.

	"""
	val = rec[col.value]
	if val not in allowed_vals:
		warn_rec (rec, "unrecognised value '%s' for field '%s'" % (val,
			col.value))


### CLASSES

class PreValidator (object):
	def __init__ (self):
		pass

	def check (self, recs):
		for r in recs:
			self.check_rec (r)
		self.check_subsections (recs)


	def check_rec (self, rec):
		"""
		Check an input record for potential problems.

		It makes sense to check for most issues here because with repetition the
		'same' error could be caught multiple times. Best to look for it in the
		source.

		"""
		check_id_length (rec)
		check_dates_and_times (rec)
		check_needs_choices (rec)
		check_choices (rec)

	def check_subsections (self, recs):
		"""
		Check that the subsections fall entirely within forms and sections.

		It is possible to write malformed subsections - subsections that overlap
		or belong to two or more forms or sections. (The way sections are written
		- automatically terminating at the end of a form - avoids this issue.) So
		it seems prudent to check that the subsections are written correctly.

		"""
		curr_form = curr_subsection = None

		# for every record
		for r in recs:
			new_subsection = r[COL.subsection.value]

			if curr_subsection:
				# currently in subsection

				if curr_subsection == new_subsection:
					# still in same section
					new_form = r[COL.subsection.value]
					new_section = r[COL.section_header.value]
					# ... form should be the same
					if curr_form != new_form:
						msg = "subsection '%s' crosses form boundaries" % \
							curr_subsection
						error_rec (r, msg)
					# ... section should be blank
					if new_section:
						msg = "subsection '%s' crosses section boundaries" % \
							curr_subsection
						error_rec (r, msg)

				elif new_subsection:
					# starting new subsection
					curr_subsection = new_subsection
					curr_form = rec[i][COL.form_name.value]

				else:
					# finished subsection and moving to non-subsection
					curr_form = curr_subsection = None

			else:
				# currently _not_ in subsection

				if new_subsection:
					# started a subsection
					curr_subsection = new_subsection
					curr_form = r[COL.form_name.value]
				else:
					# still not in subsection
					pass


class PostValidator (object):
	# TODO: am I checking for unique ids twice?
	def __init__ (self):
		self.field_ids = []
		self.form_names = []
		self.ids = []

	def check (self, recs):
		for r in recs:
			self.check_rec (r)

	def check_unique_id (self, rec):
		variable = rec[COL.variable.value]
		if variable in self.ids:
			warn_rec (rec, "duplicate id '%s'" % (variable))
		else:
			self.ids.append (variable)

	def check_form_name (self, rec):
		"""
		Ensure form names are not duplicated and run consecutively.

		"""
		# NOTE: we actually can't tell the difference between duplicated form
		# names and non-consecutive forms - it's all in the eye of the beholder -
		# so it creates the same error
		# NOTE: check for required form_name elsewhere
		form_name = rec[COL.form_name.value]
		if form_name in self.form_names:
			if form_name != self.form_names[-1]:
				error_rec (rec, "form '%s' occurs non-consecutively")
		else:
			self.form_names.append (form_name)

	def check_rec (self, rec):
		check_required_fields (rec)
		check_id_length (rec)
		self.check_unique_id (rec)
		self.check_form_name (rec)

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
			error_rec (rec, "variable '%s' duplicated" % var_name)
		else:
			self.field_ids.append (rec[COL.variable.value])

		# check bl vars are proper
		bl_str = rec[COL.branching_logic.value]
		var_names = [m for m in BL_STR_VAR_REGEX.finditer (bl_str)]
		for m in var_names:
			curr_var = m.groups()[0]
			if curr_var not in self.field_ids:
				warn_rec (rec, "unrecognised variable '%s' in branching logic" % curr_var)





### END ###
