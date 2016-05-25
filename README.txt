simpleredcapbuilder
===================

Background
----------

REDCap is a fabulously useful tool for creating web databases, including a
useful scheme for defining the database schema ("data dictionaries") in plain
CSV files. However, difficulties arise when designing complex schema. It
is cumbersome to code multiuple occurences of essentially the same field (e.g.
``sample_1 ... sample_2 ...``). If changes need to be made, keeping wording and
behaviour consistent across multiple instances is tedious. If a number of
similar databases have to be deployed, the consistency problem is multipled.

``simpleredcapbuilder`` allows you to write REDCap schema in a more compact
form that allows for repetition of rows, sections and forms (instruments), with
straightforward text substitution into the repeats. It allows make checks on
the schema, looking for possibly invalid values.


Using simpleredcapbuilder
-------------------------

simpleredcapbuilder installs a single script, that is called::

	usage: expand-redcap-schema [-h] [-o OUTFILE] infile

	positional arguments:
	  infile                compact REDCap file to be processed

	optional arguments:
	  -h, --help            show this help message and exit
	  -o OUTFILE, --outfile OUTFILE
	                        output expanded redcap data dictionary

This accepts a "compact" REDCap data dictionary, which actually follows the
form of the standard data dictionary with two additional columns: ``tags`` and
``repeat``. (Note: the ``tags`` column is not currently used.). The ``repeat``
column says whether the row, or section or form starting with that row, should
be repeated. For example:

* ``1-7``
* ``item: 'A', 'B', 'C'``
* ``section: 'foo', 'bar', 'baz'``
* ``form: (1, 'one'), (2, 'two'), (3, 'three')``

That is, the repeat element starts with a qualifier saying whether the repeat is
for the row, section or form. If no qualifier is given, it is assumed to be for the item. This is followed by either a range of numbers, or a sequence of values.

When this data dictionary is expanded, the associated items will be repeated. 



Design and development
----------------------

There's a lot of value in making a more powerful and more compact schema for
REDcap databases, but a lot of conflicting forces. The simple addition of a
few columns seems the best solution, you can easily make an old schema into
the new format with minial modification. This does set up a lot of parsing
issues (e.g. telling the difference between repetition of the rows and
sections). The qualifiers seem to simple solve this problem. 

This approach allowed me to collapse a 3000 item data dictionary down into less than 600 rows, with a commensurate consistency in how items were named and
behaved. 

Note that Excel strips leading single quotes from strings, which is a delightful behaviour.



