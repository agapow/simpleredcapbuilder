"""
Take the structure of an compact data dictionary and use it to render a dd.
"""

### IMPORTS

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import object
from builtins import open
from future import standard_library
standard_library.install_aliases()

import csv

from jinja2 import Template, Undefined, StrictUndefined, DebugUndefined
from jinja2 import exceptions as jexcept

from . import consts
from . import jext
from . import utils


### CONSTANTS & DEFINES

_TEMPLATE_PTH = 'schema.tmp'


### CODE ###

class ExpandDbSchema (object):
	def __init__ (self):
		pass

	def write (self, s):
		self.out_hndl.write (s)

	def expand (self, db_schema, inc_tags=False, exc_tags=False,
			out_pth=_TEMPLATE_PTH):
		self.db_schema = db_schema
		self.inc_tags, self.exc_tags = inc_tags, exc_tags
		assert not (inc_tags and exc_tags), "cannot have included and excluded tags"
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

		self.start_tags (f)
		if f['repeat']:
			self.write ("{%% for f_iter in %s -%%}\n" % f['repeat'])

		for x in f['contents']:
			dtype = x.get ('type', None)
			if dtype  == 'item':
				self.expand_item (x)
			elif dtype  == 'section':
				self.expand_section (x)
			else:
				assert False, "unrecognised type '%s'" % dtype

		if f['repeat']:
			self.write ("{% endfor -%}\n")
		self.end_tags (f)

	def expand_section (self, s):
		assert s['type'] == 'section', "expected section but got '%s'" % s['type']
		self.curr_section_name = s['name']

		self.start_tags (s)
		if s['repeat']:
			self.write ("{%% for s_iter in %s -%%}\n" % s['repeat'])

		for x in s['contents']:
			assert x['type'] == 'item', "expected item but got '%s'" % x['type']
			self.expand_item (x)

		if s['repeat']:
			self.write ("{% endfor -%}\n")
		self.end_tags (s)

	def expand_item (self, itm):
		assert itm['type'] == 'item', "expected item but got '%s'" % itm['type']

		self.start_tags (itm)
		if itm['repeat']:
			self.write ("{%% for i_iter in %s -%%}\n" % itm['repeat'])

		self.csv_writer.writerow (itm)

		if itm['repeat']:
			self.write ("{% endfor -%}\n")
		self.end_tags (itm)

	def start_tags (self, item):
		if item['tags']:
			if self.inc_tags:
				self.write ("{%% if are_any_tags_selected (%s, tags) -%%}\n" %
					item['tags'])
			elif self.exc_tags:
				self.write ("{%% if not are_any_tags_selected (%s, tags) -%%}\n" %
					item['tags'])

	def end_tags (self, item):
		if item['tags'] and (self.inc_tags or self.exc_tags):
			self.write ("{% endif -%}\n")


from jinja2 import Undefined

class AlertUndefined (Undefined):
	'''
	When an undefined var found, give alert but keep going
	'''
	def _fail_with_undefined_error (self, *args, **kwargs):
		utils.warn ('JINJA2: something was undefined!')
		print (dir (self))
		return None


def render_template (tmpl_str, render_vals={}):
	template = Template (tmpl_str, undefined=AlertUndefined)
	# XXX: allow for external vars to be passed in
	render_vals.update (jext.EXT_DICT)
	try:
		rendered_tmpl = template.render (**render_vals)
		return rendered_tmpl
	except jexcept.UndefinedError as err:
		print ('variable used in schema is undefined')
		raise



### END ###
