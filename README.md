TweeQL makes interacting with the Twitter API as easy as SQL!

For example, the TweeQL query `SELECT brand(text) AS brand,
sentiment(text) AS sentiment FROM twitter_sample;` will run two
user-defined functions, `brand` and `sentiment` to extract brand names and
expressed user sentiment from the text of every tweet that passes through
the Twitter Streaming API.

LICENSE
=======
BSD license

Projects on which TweeQL Depends
================================
tweepy---Twitter API
pyparsing---For the SSQL parsing
sqlalchemy---For putting results into a relational database
ordereddict---For creating an LRU cache of keys (geoloc cache)
geopy---For geolocation
nltk---For sentiment analysis
