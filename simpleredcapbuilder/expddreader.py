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
from builtins import range
from builtins import int
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import object

import csv
import os
from ast import literal_eval as leval

from . import consts
from .consts import Column, ALL_NAMES
from .validation import pre_validate

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
			if hasattr (self, '_in_hndl'):
				self._in_hndl.close()

	def parse (self):
		rdr = csv.DictReader (self._in_hndl)
		# check fieldnames in input
		legal_fld_names = []
		for in_fld in rdr.fieldnames:
			assert in_fld in ALL_NAMES, "unrecognised input column '%s'" % in_fld
		recs = [self.pre_process (r) for r in rdr]
		return self.parse_all_recs (recs)

	def pre_process (self, rec):
		"""
		Parse out the additional fields in each record.
		"""
		try:
			rec['tags'] = self.parse_tags_str (rec.get ('tags', ''))
			rec['repeat'] = self.parse_repeat_str (rec.get ('repeat', ''))
			return rec
		except:
			print ("Rec %s has problems with its repeat or tag fields" % rec[Column.variable.value])
			raise

	def parse_metadata_qual (self, md_str):
		"""
		Extract the form / section / item qualifier off record str
		"""
		if ';' in md_str:
			# multiple metadata statements
			md_statements = [x.strip() for x in md_str.split(';')]
		else:
			# single statement
			md_statements = [md_str.strip()]

		# now parse statements
		md_dict = {'form': [], 'section': [], 'item': []}
		for md_st in md_statements:
			if ':' in md_st:
				qual, val = [x.strip() for x in md_st.split(':', 1)]
				assert qual in ('form', 'section', 'item'), \
					"unrecognised qualifier '%s'" % qual
			else:
				qual = 'item'
				val = md_st.strip()
			assert not md_dict[qual], \
				"multiple statements for '%s' in '%s'" % (qual, md_statements)
			md_dict[qual] = val

		return md_dict

	def parse_tags_str (self, s):
		"""
		Parse out the 'tags' field in each record.
		"""
		if not s:
			return {'form': [], 'section': [], 'item': []}
		else:
			md_dict = self.parse_metadata_qual (s)
			for k, v in list (md_dict.items()):
				if v:
					md_dict[k] = [x.strip() for x in v.split(',')]
			return md_dict

	def parse_repeat_str (self, s):
		"""
		Parse out the 'repeat' field in each record.
		"""
		if not s:
			return {'form': [], 'section': [], 'item': []}
		else:
			md_dict = self.parse_metadata_qual (s)
			for k, v in list (md_dict.items()):
				if not v:
					continue
				elif ',' in v:
					# must be a explicit sequence
					# hideous but I eval the string to get a list
					try:
						rpt_list = leval ("[%s]" % v)
					except Exception as err:
						print ("eval string")
						print (v)
						raise
				else:
					assert '-' in v, "can't interpret '%s' as range" % v
					start, stop = [int (x) for x in v.split ('-', 1)]
					rpt_list = list (range (start, stop+1))

				md_dict[k] = rpt_list

			assert len (md_dict) == 3, "bad dict %s" % md_dict
			return md_dict



	def parse_all_recs (self, recs):
		"""
		Parse records to return a list of forms.
		"""
		all_forms = []

		num_recs = len (recs)

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
		pre_validate (rec)
		return rec


### END ###
