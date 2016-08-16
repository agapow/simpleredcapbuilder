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

simpleredcapbuilder produces a standard REDCap data dictionary from a "compact"
form. This compact dictionary follows the form of the standard but with two
additional columns: ``repeat`` and ``tags``. These allow rows, sections or forms
to be repeated or to be optionally included. Also, a templating language can be
used to embed expressions in the compact input, allowing simple logical
substitutions and text expansions.  Finally, files of external values
can be defined (e.g. choices, validation types, minimums and maximums) and used
in the compact dictionary, being substituted during the expansion.

This allows REDCap data dictionaries to be expressed more compactly and more easily:

* A repeating row or section need only be defined once (e.g. ``sample_1``, ``sample_2`` ...)
* The templating language can be used to write the branching logic for the repeats
* Files of included variables can be used to centrally define values that are used multiple times, so they only need to be defined once and can be kept consistent.
* Tags can be used to produce related databases from the one file or keep parts under development separate.


Using simpleredcapbuilder
-------------------------

simpleredcapbuilder installs a single script, that is called::

	expand-redcap-schema [-h] [-o OUTFILE] [-i INCLUDE_TAGS]
									[-x EXCLUDE_TAGS] [-n] [-v INCLUDE_VARS]
									infile

	positional arguments:
	  infile                compact REDCap file to be processed

	optional arguments:
	  -h, --help            show this help message and exit
	  -o OUTFILE, --outfile OUTFILE
									output expanded redcap data dictionary
	  -i INCLUDE_TAGS, --include-tags INCLUDE_TAGS
									only include untagged sections or those with this tag
	  -x EXCLUDE_TAGS, --exclude-tags EXCLUDE_TAGS
									exclude sections with this tag
	  -n, --name            name the output file for the tags passed in
	  -v INCLUDE_VARS, --include-vars INCLUDE_VARS
									include external file of variables

The file ``USAGE.txt`` includes more detailed instructions and examples can be
found in the ``examples`` dir.
