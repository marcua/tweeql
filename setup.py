#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
import tweeql

setup(name="tweeql",
      version=tweeql.__version__,
      description="A SQL-like query language for the Twitter API",
      license="BSD",
      author="Adam Marcus",
      author_email="marcua@marcua.net",
      url="http://github.com/marcua/tweeql",
      packages = find_packages(),
      scripts = ['tweeql/bin/tweeql-command-line.py'],
      install_requires = ['pyparsing>=1.5.2', 'sqlalchemy>=0.6.1', 'ordereddict', 'geopy'],
      keywords= "twitter query sql library",
      zip_safe = True)
