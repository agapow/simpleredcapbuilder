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

This accepts a "compact" REDCap data dictionary, which allows which actually
follows the form of the standard data dictionary with two additional columns:
``tags`` and ``repeat``. (Note: the ``tags`` column is not currently used.). The
``repeat`` column says whether the row, or section or form starting with that
row, should be repeated. For example:

* ``1-7``
* ``item: 'A', 'B', 'C'``
* ``section: 'foo', 'bar', 'baz'``
* ``form: (1, 'one'), (2, 'two'), (3, 'three')``
* ``item: 3-4; form: 'low', 'high'``

That is, the repeat element starts with a qualifier saying whether the repeat is
for the row, section or form. If no qualifier is given, it is assumed to be for
the item. This is followed by either a range of numbers, or a sequence of
values. (The sequence is anything that when enclosed in square braces will look
like a legal list to Python.) Multiple qualifiying statement may be seperated by
a semicolon.

When this data dictionary is expanded, the associated items will be repeated.
See the example ``simple-but-useless`` for an illustration.

Obviously, simply repeating a row or section is useless: variable identifiers
will be repeated, fields will have the same name, etc. simpleredcapbuildergets
around this problem by embedding and interpreting a template language (jinja2)
in the data dictionary. For example, an item may have the repeat value of
``item: 1-3`` and the variable name of ``sample_{{ i_iter }}`` and the field
label of ``Sample number {[ i_iter ]}``. These will result in three rows, named
and labelled::

	sample_1 ... Sample number 1
	sample_2 ... Sample number 2
	sample_3 ... Sample number 3

The sequence of values used in any repeat loop are ``i_iter``, ``s_iter`` and
``f_iter`` for item, section and form repeats respectively. See the example ``simple-and-useful`` for an illustration.

More complex transformations are possible and you are referred to the Jinja documentation.

Items, sections and forms can be optionally included in an expanded schema by the use of tags. Basically, tags allow pieces of the form to be labelled and any expansion to selectively include pices of the form with a given label. The 'tags' column of the schema follows a similar form to the 'repeat':

* ``foo``
* ``item: foo``
* ``section: foo, bar, baz; form: quux``

That is, the tags element starts with a qualifier saying whether the tag list is
for the row, section or form. If no qualifier is given, it is assumed to be for
the item. This is followed by a single word/symbol or a comma separated list of
words/symbols. Multiple qualifying statement may be separated by a semicolon.

Tags are selected for inclusion with the commandline flag ``-i/--include-tags``. Multiple tags are selected with multiple uses of this flag. The following logic is used for deciding which items are included:

* By default, all items are selected. But if any tags are selected (i.e. the ``-i`` flag is used at least once), then only the untagged items are automatically included.

* Items with the corresponding tag are included.

* Enclosed items (e.g. sections and items within forms) that are not included will not be included either.

* Having any selected tag will lead to an item being included - it doesn't need to have all the selected tags. 

See the example ``simple-and-tagged`` for an illustration. Note that the ``-n`` flag is useful for labelling the output of selectively tagged schema.


Various tips
------------

Note that Excel strips leading single quotes from strings, which is a delightful behaviour.

simpleredcapbuilder leaves a few intermediate files that may be useful for
debugging output or understanding how it works:

* ``.json``: a representation of the structure of the compact data dictionary
* ``.jinja``: the data dictionary rendered into a
* ``.expanded.csv``: the final rendered form for upload into REDCap

Sometimes you need to repeat a small set of fields that are less than a whole section, e.g. a sample date and volume, a person and their affiliation, etc.
it's possible to use jinja to to produce a "fake" (invisible) section that will
be repeated. Jinja tags of the form ``{# ... #}`` will produce no output, and can thus be used as a section header. So you could title a section ``{# fakesection sample-date #}`` and repeat it, without it appearing as a section in the output. Note that you still can't have a repeating fake section inside a repeating section.

If you want to expand a schema using only the untagged fields, use the '-i' flag with a tag that doesn't exist, e.g.::

	% expand-redcap-schema -i dummytag myschema.csv

Note that tags don't have to be quoted like list items in the repeat field. IN fact, if you do quote them, it would probably be difficult to pass the tag name on the commandline.

Almost inevitably, after writing this I find that someone else had the same thought: https://github.com/chop-dbhi/redcap-repeat. It looks like a much simpler and user-friendly solution, albeit not as powerful but suitable for many use cases.


References
----------

* `simpleredcapbuilder code repository <https://github.com/agapow/simpleredcapbuilder>`__

* `Jinja2 templating system <http://jinja.pocoo.org/>`__
