simpleredcapbuilder
===================

Background
----------

REDCap is a fabulously useful tool for creating web databases, including a
useful scheme for defining the database schema ("data dictionaries") in plain
CSV files. However, difficulties arise when designing complex schema. It
is cumbersome to code multiple occurrences of essentially the same field (e.g.
``sample_1 ... sample_2 ...``). If changes need to be made, keeping wording and
behaviour consistent across multiple instances is tedious. If a number of
similar databases have to be deployed, the consistency problem is multiplied.

``simpleredcapbuilder`` allows you to write REDCap schema in a more compact
form that allows for repetition of rows, sections and forms (instruments), with
straightforward text substitution into the repeats. It allows make checks on
the schema, looking for possibly invalid values.


Using simpleredcapbuilder
-------------------------

simpleredcapbuilder installs a single script, that is called::

	usage: expand-redcap-schema [-h] [-o OUTFILE] [-i INCLUDE_TAGS] [-n] infile

	positional arguments:
	  infile                compact REDCap file to be processed

	optional arguments:
	  -h, --help            show this help message and exit
	  -o OUTFILE, --outfile OUTFILE
	                        output expanded redcap data dictionary
	  -i INCLUDE_TAGS, --include-tags INCLUDE_TAGS
	                        only include untagged sections or those with this tag
	  -n, --name            name the output file for the tags passed in
