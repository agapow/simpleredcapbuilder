from setuptools import setup, find_packages
import sys, os

from simpleredcapbuilder import __version__

setup(
   name='simpleredcapbuilder',
   version=__version__,
   description="A simple and compact way to express redcap databases",
   long_description="""\
   Sometimes it can be painful to express complex REDCap databases, especially those with lots of repeating items. This package offers a way to write a REDCap data dictionary in a more compact form, allowing for repeats, optional includes and text substition.""",
   classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
   keywords='database text-processing',
   author='Paul Agapow',
   author_email='paul@agapow.net',
   url='http://www.agapow.net/software/simpleredcapbuilder',
   license='MIT',
   packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
   include_package_data=True,
   zip_safe=False,
   install_requires=[
      'jinja2',
   ],
   entry_points={
      'console_scripts': [
         'expand-redcap-schema = simpleredcapbuilder.scripts.expand:main',
      ],
   },
)
