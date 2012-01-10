#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
from setuptools import setup, find_packages
import tweeql

setup(name="tweeql",
      version=tweeql.__version__,
      description="A SQL-like query language for the Twitter API",
      license="BSD",
      author="Adam Marcus",
      author_email="tweeql@googlegroups.com",
      url="http://github.com/marcua/tweeql",
      packages = find_packages(),
      scripts = ['tweeql/bin/tweeql-command-line.py'],
      package_data = { 'tweeql' : ['extras/sentiment/sentiment.pkl.gz'] },
      install_requires = ['tweepy', 'pyparsing>=1.5.2', 'sqlalchemy>=0.6.1', 'ordereddict', 'geopy'],
      keywords= "twitter query sql library",
      zip_safe = True)
