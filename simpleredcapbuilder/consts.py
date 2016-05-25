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

# column headers
class Column (Enum):
	tags = 'tags'
	repeat = 'repeat'

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

_ALL_COLS = [x for x in Column]

META_COLS = _ALL_COLS[:2]
OUTPUT_COLS = _ALL_COLS[2:]

MANDATORY_COLS = (getattr (Column, x) for x in ['variable', 'form_name',
	'field_type', 'field_label'])


# types of items in the produced schema
class SchemaItem (Enum):
	form = 'form'
	section = 'section'
	item = 'item'



### END ###
