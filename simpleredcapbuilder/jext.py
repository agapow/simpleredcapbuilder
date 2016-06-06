"""
Jinja extensions.
"""

### IMPORTS

### CONSTANTS & DEFINES

EXT_DICT = {}


### CODE ###

def are_any_tags_selected (local_tags, selected_tags):
	for lt in local_tags:
		if lt in selected_tags:
			return True
	return False

EXT_DICT['are_any_tags_selected'] = are_any_tags_selected


### END ###
