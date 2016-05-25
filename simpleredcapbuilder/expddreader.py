"""
Read expanded REDCap data dictionary, working out the structure.


Thinking this problem out loud:
- On one hand, there's the temptation to extend the data dictionary definition
- On the other hand, it seems much more parsimonious to just add a few extra columns, so it's a valid schema if you clip off a few columns
- On the third, we run into issues with parsing here and with forms that consist purely of repeating sections (i.e. on the first item of a form, the repeats and tags refer to the form, not the item, similar problems with first item of a section).
- So it seems we need to insert special rows for the start of forms and sections, so the format is no longer a superset of the normal.
- At least this will make it easier to parseand convert from the normal.

- Note that Excel strips leading singel quotes from strings

"""

### IMPORTS

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import object

import csv
import os
from ast import literal_eval as leval

from . import consts
from .consts import Column

__ALL__ = [
	'ExpDataDictReader',
]


### CONSTANTS & DEFINES

### CODE ###

import pprint
pp = pprint.PrettyPrinter (indent=2)

def pprint (x):
	pp.pprint (x)


class ExpDataDictReader (object):
	def __init__ (self, pth_or_hndl):
		if isinstance (pth_or_hndl, ''.__class__):
			self._opened_file = True
			pth_or_hndl = open (pth_or_hndl, "r")
		else:
			self._opened_file = False
		self._in_hndl = pth_or_hndl

	def __del__ (self):
		if self._opened_file:
			self._in_hndl.close()

	def parse (self):
		rdr = csv.DictReader (self._in_hndl)
		recs = [self.pre_process (r) for r in rdr]
		return self.parse_all_recs (recs)

	def pre_process (self, rec):
		"""
		Parse out the additional fields in each record.
		"""
		rec['tags'] = self.parse_tags_str (rec.get ('tags', ''))
		rec['repeat'] = self.parse_repeat_str (rec.get ('repeat', ''))
		return rec

	def parse_metadata_qual (self, s):
		"""
		Extract the form / section / item qualifier off record str
		"""
		# XXX: need to adapt this so we can have multiple qualified lists
		if ':' in s:
			qual, val = [x.strip() for x in s.split(':', 1)]
			assert qual in ('form', 'section', 'item'), "unrecognised qualifier '%s'" % qual
			return qual, val
		else:
			return 'item', s.strip()

	def parse_tags_str (self, s):
		"""
		Parse out the 'tags' field in each record.
		"""
		null_dict = {'form': [], 'section': [], 'item': []}
		if not s:
			return null_dict
		else:
			qual, tag_str = self.parse_metadata_qual (s)
			tag_dict = {x.trim():True for x in tag_str.split(',')}
			null_dict[qual] = tag_dict
			return null_dict

	def parse_repeat_str (self, s):
		"""
		Parse out the 'repeat' field in each record.
		"""
		null_dict = {'form': [], 'section': [], 'item': []}
		if not s:
			return null_dict
		else:
			qual, rpt_str = self.parse_metadata_qual (s)
			if ',' in rpt_str:
				# must be a explicit sequence
				# hideous but I eval the string to get a list
				try:
					rpt_list = leval ("[%s]" % rpt_str)
				except Error as err:
					print ("eval string")
					print (rpt_str)
					raise
			else:
				assert '-' in rpt_str, "can't interpret '%s' as range" % rpt_str
				start, stop = [int (x) for x in rpt_str.split ('-', 1)]
				rpt_list = list (range (start, stop+1))
			null_dict[qual] = rpt_list
			return null_dict

	def parse_all_recs (self, recs):
		"""
		Parse records to return a list of forms.
		"""
		all_forms = []

		num_recs = len (recs)
		print ("Parsing %s recs ..." % num_recs)

		i = 0
		while i < num_recs:
			start = i
			form_name = recs[i][consts.Column.form_name.value]
			i += 1
			while (i < num_recs) and (recs[i][consts.Column.form_name.value] == form_name):
				i += 1
			all_forms.append (self.parse_form_recs (recs[start:i]))

		return all_forms

	def parse_form_recs (self, recs):
		form_rec = {
			'repeat': recs[0]['repeat']['form'],
			'tags': recs[0]['tags']['form'],
			'type': consts.SchemaItem.form.value,
			'name': recs[0][consts.Column.form_name.value],
			'contents': [],
		}
		num_recs = len (recs)
		i = 0

		# read initial no-section items
		while (i < num_recs) and (not recs[i][consts.Column.section_header.value]):
			form_rec['contents'].append (self.parse_item_rec (recs[i]))
			i += 1

		# now the sectioned part of the form
		while (i < num_recs):
			# start a new section
			start = i
			i += 1
			while (i < num_recs) and (not recs[i][consts.Column.section_header.value]):
				i += 1
			form_rec['contents'].append (self.parse_section_recs (recs[start:i]))

		return form_rec

	def parse_section_recs (self, recs):
		section_rec = {
			'repeat': recs[0]['repeat']['section'],
			'tags': recs[0]['tags']['section'],
			'type': consts.SchemaItem.section.value,
			'name': recs[0][consts.Column.section_header.value],
			'contents': [],
		}

		for r in recs:
			section_rec['contents'].append (self.parse_item_rec (r))

		return section_rec

	def parse_item_rec (self, rec):
		rec['type'] = 'item'
		rec['repeat'] = rec['repeat']['item']
		rec['tags'] = rec['tags']['item']
		self.validate_rec (rec)
		return rec



	def validate_rec (self, rec):
		rec_id = rec[Column.variable.value]

		def invalid_msg (msg):
			print ("Record %s is possibly invalid: %s" % (rec_id, msg))

		if rec[Column.field_type.value] in ('radio', 'checkbox', 'dropdown'):
			if not rec[Column.choices_calculations.value].strip():
				invalid_msg ("radio or checkbox has no choices")
			if rec[Column.text_validation_type.value].strip():
				invalid_msg ("radio or checkbox has text validation")
			if rec[Column.text_validation_min.value].strip():
				invalid_msg ("radio or checkbox has text min")
			if rec[Column.text_validation_max.value].strip():
				invalid_msg ("radio or checkbox has text max")

		if rec[Column.field_type.value] not in ('radio', 'checkbox', 'dropdown'):
			if rec[Column.text_validation_type.value] not in ('number', 'integer'):
				if rec[Column.choices_calculations.value].strip():
					invalid_msg ("non-radio / checkbox / numeric has choices or calculation")
					print ("*%s*" % rec[Column.choices_calculations.value].strip())

		if ('date' in rec[Column.field_label.value].lower()) or ('date' in rec[Column.variable.value].lower()):
			if 'date' not in rec[Column.text_validation_type.value]:
				invalid_msg ("looks like date but has no date validator")

		if ('time' in rec[Column.field_label.value].lower()) or ('time' in rec[Column.variable.value].lower()):
			if 'time' not in rec[Column.text_validation_type.value]:
				invalid_msg ("looks like time but has no date validator")

		choices = rec[Column.choices_calculations.value].strip()
		if choices and '|' in choices and ',' in choices:
			for cp in [x.strip() for x in choices.split('|')]:
				if ',' not in cp:
					invalid_msg ("malformed choice string '%s'" % cp)
				else:
					if cp.count (',') != 1:
						invalid_msg ("malformed choice string '%s'" % cp)

				# else:
				# 	val_str, label_str = [x.strip() for x in cp.split(',', 1)]
				# 	if ' ' in cp:
				# 		invalid_msg ("illegal character in choice value '%s'" % val_str)


def render_template (tmpl_str):
	from jinja2 import Template
	template = Template (tmpl_str)
	return template.render ()







### END ###
