"""
Module-wide constants.
"""

### IMPORTS

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from enum import Enum


### CONSTANTS & DEFINES

class FileType (Enum):
	# file type and list of acceptable extensions
	csv = ('csv',)
	xls = ('xls',)
	xlsx = ('xlsx',)

	@classmethod
	def from_path (cls, pth):
		"""
		Sniff the file type from a file path (extension).

		This method is case-insensitive and will work off raw extensions.
		"""
		pth = pth.lower()
		for member in cls:
			for ext in member.value:
				if pth.endswith ('.%s' % ext):
					return member
		raise ValueError ("can't recognise file type of '%s'" % pth)


# column headers
class Column (Enum):
	tags = 'tags'
	repeat = 'repeat'
	subsection = 'subsection'

	variable = 'Variable / Field Name'
	form_name = 'Form Name'
	section_header = 'Section Header'
	field_type = 'Field Type'
	field_label = 'Field Label'
	choices_calculations = 'Choices, Calculations, OR Slider Labels'
	field_note = 'Field Note'
	text_validation_type = 'Text Validation Type OR Show Slider Number'
	text_validation_min = 'Text Validation Min'
	text_validation_max = 'Text Validation Max'
	identifier = 'Identifier?'
	branching_logic = 'Branching Logic (Show field only if...)'
	required_field = 'Required Field?'
	custom_alignment = 'Custom Alignment'
	question_number = 'Question Number (surveys only)'
	matrix_group_name = 'Matrix Group Name'
	matrix_ranking = 'Matrix Ranking?'
	field_annotation = 'Field Annotation'

ALL_COLS = [x for x in Column]
ALL_NAMES = [x.value for x in ALL_COLS]

META_COLS = ALL_COLS[:3]
OUTPUT_COLS = ALL_COLS[3:]

MANDATORY_COLS = (getattr (Column, x) for x in ['variable', 'form_name',
	'field_type', 'field_label'])


# types of items in the produced schema
class SchemaItem (Enum):
	form = 'form'
	section = 'section'
	subsection = 'subsection'
	row = 'row'


ALLOWED_FTYPE_VALS = [
	'calc',
	'checkbox',
	'description',
	'dropdown',
	'file',
	'notes',
	'radio',
	'slider',
	'sql',
	'text',
	'truefalse',
	'yesno',
]

ALLOWED_VALIDATION_VALS = [
	'date',
	'date_dmy',
	'date_mdy',
	'date_ymd',
	'datetime_dmy',
	'datetime_mdy',
	'datetime_seconds_dmy',
	'datetime_seconds_mdy',
	'datetime_seconds_ymd',
	'datetime_ymd',
	'email',
	'integer',
	'number',
	'number_1dp',
	'number_2dp',
	'phone',
	'time',
	'zipcode',
	'',
]

ALLOWED_IDENTIFIER_VALS = [
	'Y',
	'',
]

ALLOWED_REQUIRED_VALS = [
	'Y',
	'',
]


### END ###
