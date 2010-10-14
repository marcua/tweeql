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

    marcua@marcua-x60:~$ tweeql-command-line.py
    TWITTER_USERNAME and TWITTER_PASSWORD not defined in settings.py
    Twitter username: marcuatest3
    Twitter password:
    tweeql>

Once at the `tweeql>` command line, you can enter SQL-like queries, which will hit the Twitter Streaming API.

To see Tweets from the Twitter's gardenhose, type `SELECT text FROM twitter_sample;`:

    tweeql> SELECT text from twitter_sample;
    não sei realmente o que decidir da minha vida.. muito confusa. :S
    伝線した黒ストッキングの使い道は…`

These should stream by your screen relatively quickly.  Hit `ctrl+c` to stop the query.  To exit TweeQL, hit `ctrl+c` again.

Queries by Example
==================
TWITTER vs. TWITTER_SAMPLE
--------------------------
In the last

Finally, check out [http://github.com/marcua/tweeql/blob/master/examples/examples.txt] for a list of example queries that you can run in TweeQL.

Saving Tweets to a Database
===========================

Programmatic Access
===================
Working from the TweeQL command-line is a good way to get started, but you might want to issue TweeQL queries programmatically.

Here's a simple code sample to get started from, also available at [http://github.com/marcua/tweeql/blob/master/examples/tweeql-programmatic.py]:

    from tweeql.exceptions import TweeQLException
    from tweeql.query_runner import QueryRunner

    runner = QueryRunner()
    runner.run_query("SELECT text FROM twitter_sample;", False)

That's it!  `QueryRunner.run_query` takes a TweeQL query and executes it.  The second argument to `run_query` determines whether the query runs asynchronously or not.  In this case, the program blocks on the `run_query` call because the second argument is `False`.  If you run with the second argument as `True`, a new thread will execute the query.  To stop the query programmatically, use `runner.stop_query()`.

User-Defined Functions (UDFs)
=============================
The examples we have shown have used several user-defined functions (`sentiment`, `tweetLatLng`, etc.).  If you wish to write your own UDF, you can do so in python.  The following example, in which we count the length of tweets on the gardenhose, can be found at [http://github.com/marcua/tweeql/blob/master/examples/tweeql-udf.py]:

    from tweeql.exceptions import TweeQLException
    from tweeql.field_descriptor import ReturnType
    from tweeql.function_registry import FunctionInformation, FunctionRegistry
    from tweeql.query_runner import QueryRunner

    class StringLength():
        return_type = ReturnType.INTEGER

        @staticmethod
        def factory():
            return StringLength().strlen

        def strlen(self, tuple_data, val):
            """ 
                Returns the length of val, which is a string
            """
            return len(val)

    fr = FunctionRegistry()
    fr.register("stringlength", FunctionInformation(StringLength.factory, StringLength.return_type))

    runner = QueryRunner()
    runner.run_query("SELECT stringlength(text) AS len FROM twitter_sample;", False)

In this example, we build the class `StringLength`, which has two methods: a `factory` method and an `strlen` method.  Stricly speaking, the only method that a UDF requires is a `factory` method---this is the method that returns another method (in this case `stringlength`) which performs the actual computation.  The only requirement for the UDF computation method is that its first argument be `tuple_data`, a dictionary of data that is returned with all tweets (read more about this [here](http://mehack.com/map-of-a-twitter-status-object)).

You can include any number of arguments after `tuple_data`.  In our case, we only take one: the string `val` which we wish to take the length of.  Note that when we run the query on the last line of this example, we pass `text` as an argument to `stringlength`---this is the value that `val` will take on.

After we have defined our UDF in `StringLength`, we then register the function.  To do this, we create a `FunctionRegistry`, which is a singleton, and register the function to the TweeQL `stringlength` function.  You can see the `stringlength` function in action on the last line of this example: it's a first-class citizen in our queries now!

To see more UDFs, take a look at http://github.com/marcua/tweeql/blob/master/tweeql/builtin_functions.py.

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
