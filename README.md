TweeQL makes interacting with the Twitter API as easy as SQL makes it to interact with relational data!

For example, the TweeQL query `SELECT brand(text) AS brand,
sentiment(text) AS sentiment FROM twitter_sample;` will run two
user-defined functions, `brand` and `sentiment` to extract brand names and
expressed user sentiment from the text of every tweet that passes through
the Twitter Streaming API.  All this, without having to worry about the details
of implementing the API correctly.

Installation
============
There are two options for installing TweeQL:
1. *easy_install/pip*.  Something like `sudo easy_install tweeql` or `sudo pip install tweeql` at the command line should suffice.
1. *from github*.  After checking out this repository, run `python setup.py install` to install!

Initializing your Settings
==========================
TweeQL requires a `settings.py` to be in your current working directory before
you can use it.  The simplest way to get a working `settings.py` file is to get the template into your current directory:


`wget http://github.com/marcua/tweeql/raw/master/setting.py.template -O settings.py`

This file should work without editing.  You can edit it to provide a username/password for the streaming API, or to change the database into which extracted data will be inserted.

A first example
===============
After installing TweeQL, you should be able to run the TweeQL command line by typing `tweeql-command-line.py`:

`marcua@marcua-x60:~$ tweeql-command-line.py`  
`TWITTER_USERNAME and TWITTER_PASSWORD not defined in settings.py`  
`Twitter username: marcuatest3`  
`Twitter password:`  
`tweeql>`

You can edit `settings.py` to save your username and password.

Once at the `tweeql>` command line, you can enter SQL-like queries, which will hit the Twitter Streaming API.

To see Tweets from the Twitter's gardenhose, type `SELECT text FROM twitter_sample`:  
`tweeql> SELECT text from twitter_sample;  
não sei realmente o que decidir da minha vida.. muito confusa. :S  
伝線した黒ストッキングの使い道は…`  

These should stream by your screen relatively quickly.  Hit `ctrl+c` to stop the query.  To exit TweeQL, hit `ctrl+c` again.

Queries by Example
==================

Saving Tweets to a Database
===========================

More Examples
=============

Projects on which TweeQL Depends
================================
tweepy---Twitter API in Python.  TweeQL would not exist without Tweepy!
pyparsing---For the SSQL parsing
sqlalchemy---For putting results into a relational database
ordereddict---For creating an LRU cache of keys (geoloc cache)
geopy---For geolocation
nltk---For sentiment analysis

License
=======
TweeQL is BSD-licensed.  Do what you will with it, but be nice!
