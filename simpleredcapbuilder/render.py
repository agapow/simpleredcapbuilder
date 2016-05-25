"""
Take the structure of an compact data dictionary and use it to render a dd.
"""

### IMPORTS

import csv

from . import consts


### CONSTANTS & DEFINES

_TEMPLATE_PTH = 'schema.tmp'


### CODE ###

class ExpandDbSchema (object):
	def __init__ (self):
		pass

	def write (self, s):
		self.out_hndl.write (s)

	def expand (self, db_schema, out_pth=_TEMPLATE_PTH):
		self.db_schema = db_schema
		with open (out_pth, 'w') as out_hndl:
			self.out_hndl = out_hndl
			self.csv_writer = csv.DictWriter (out_hndl,
				fieldnames=[x.value for x in consts.OUTPUT_COLS],
				extrasaction='ignore',
			)
			self.csv_writer.writeheader()

			for f in self.db_schema:
				self.expand_form (f)

	def expand_form (self, f):
		assert f['type'] == 'form', "expected form but got '%s'" % f['type']
		self.curr_form_name = f['name']

		if f['repeat']:
			self.write ("{%% for f_iter in %s -%%}\n" % f['repeat'])

		for x in f['contents']:
			dtype = x.get ('type', None)
			if dtype  == 'item':
				self.expand_item (x)
			elif dtype  == 'section':
				self.expand_section (x)
			else:
				print (x)
				assert False, "unrecognised type '%s'" % dtype

		if f['repeat']:
			self.write ("{% endfor -%}\n")

	def expand_section (self, s):
		assert s['type'] == 'section', "expected section but got '%s'" % s['type']
		self.curr_section_name = s['name']

		if s['repeat']:
			self.write ("{%% for s_iter in %s -%%}\n" % s['repeat'])

		for x in s['contents']:
			assert x['type'] == 'item', "expected item but got '%s'" % x['type']
			self.expand_item (x)

		if s['repeat']:
			self.write ("{% endfor -%}\n")

	def expand_item (self, itm):
		assert itm['type'] == 'item', "expected item but got '%s'" % itm['type']

		if itm['repeat']:
			self.write ("{%% for i_iter in %s -%%}\n" % itm['repeat'])

		self.csv_writer.writerow (itm)

		if itm['repeat']:
			self.write ("{% endfor -%}\n")




### END ###
