"""
Read expanded REDCap data dictionary, working out the structure.


Thinking this problem out loud:
- On one hand, there's the temptation to extend the data dictionary definition
- On the other hand, it seems much more parsimonious to just add a few extra columns, so it's a valid schema if you clip off a few columns
- On the third, we run into issues with parsing here and with forms that consist purely of repeating sections (i.e. on the first item of a form, the repeats and tags refer to the form, not the item, similar problems with first item of a section).
- So it seems we need to insert special rows for the start of forms and sections, so the format is no longer a superset of the normal.
- At least this will make it easier to parseand convert from the normal.

- Note that Excel strips leading single quotes from strings

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
from .consts import Column, ALL_NAMES, MANDATORY_COLS
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

	def read_file (self, in_pth):
		filetype = consts.FileType.from_path (in_pth)

		if filetype is consts.FileType.csv:
			# read csv file
			with open (in_pth, 'r') as in_hndl:
				rdr = csv.DictReader (in_hndl)
				recs = [r for r in rdr]
				return (rdr.fieldnames, recs)
		else:
			# otherwise read excel file
			# grab the first sheet
			import xlrd
			wb = xlrd.open_workbook (in_pth)
			sht = wb.sheet_by_index (0)

			# work out dimensions
			# TODO: bulletproof against excess cols & rows
			# TODO: allow not all rows to be defined
			col_cnt = sht.ncols
			row_cnt = sht.nrows

			# get fieldnames
			fieldnames = [sht.cell (0, i).value for i in range (col_cnt)]

			# get records
			recs = []
			for i in range (1, row_cnt):
				new_rec = {}
				for j in range (col_cnt):
					new_rec[fieldnames[j]] = sht.cell (i, j).value
				recs.append (new_rec)

			# return
			return (fieldnames, recs)

	def parse (self, in_pth, extra_cols=True):
		fieldnames, recs = self.read_file (in_pth)

		# if extra columns not allowed, check they aren't there
		if not extra_cols:
			for in_fld in fieldnames:
				assert in_fld in ALL_NAMES, "unrecognised input column '%s'" % in_fld

		# check required cols are there
		for c in MANDATORY_COLS:
			assert c.value in fieldnames, "missing required column '%s'" % c.value

		# parse out structured fields
		proc_recs = [self.pre_process (r) for r in recs]

		## Return:
		return self.parse_all_recs (proc_recs)

	def pre_process (self, rec):
		"""
		Clean flanking whitespace, ensure rec has all fields and parse out structured new fields.
		"""
		# make sure that every field is in the record
		for f in consts.ALL_NAMES:
			if rec.haskey (f):
				rec[f] = rec[f].strip()
			else:
				rec[f] = ''

		# now parse out the structured / metadata fields
		try:
			rec['tags'] = self.parse_tags_str (rec.get ('tags', ''))
			rec['repeat'] = self.parse_repeat_str (rec.get ('repeat', ''))
			return rec
		except:
			print ("Rec %s has problems with its repeat or tag fields" % rec[Column.variable.value])
			raise
		if rec[Column.text_validation_type.value] == 'integer':
			min = rec[Column.text_validation_min.value]
			if min:
				rec[Column.text_validation_min.value] = str ("%d" % int (min))
			max = rec[Column.text_validation_max.value]
			if max:
				rec[Column.text_validation_max.value] = str ("%d" % int (max))

	def parse_metadata_qual (self, md_str):
		"""
		Extract the form / section / etc. qualifier off record str
		"""
		if ';' in md_str:
			# multiple metadata statements
			md_statements = [x.strip() for x in md_str.split(';')]
		else:
			# single statement
			md_statements = [md_str.strip()]

		# now parse statements
		md_dict = {'form': [], 'section': [], 'subsection': [], 'row': []}
		for md_st in md_statements:
			if ':' in md_st:
				qual, val = [x.strip() for x in md_st.split(':', 1)]
				assert qual in ('form', 'section', 'subsection', 'row'), \
					"unrecognised qualifier '%s'" % qual
			else:
				qual = 'row'
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
			return {'form': [], 'section': [], 'subsection': [], 'row': []}
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
			return {'form': [], 'section': [], 'subsection': [], 'row': []}
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

		## Return:
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

		## Return:
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
			section_rec['contents'].append (self.parse_row_rec (r))

		## Return:
		return section_rec

	def parse_row_rec (self, rec):
		rec['type'] = 'row'
		rec['repeat'] = rec['repeat']['row']
		rec['tags'] = rec['tags']['row']
		pre_validate (rec)

		## Return:
		return rec


### END ###
