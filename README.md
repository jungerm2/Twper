# Twper - an asynchronous twitter scraper

Twitter provides a powerful REST and Streaming API. With the REST API, you can only send 
about 720 requests per hour and only get tweets that are less than a week old. This project 
tries to overcome these limitations by scraping the website instead. This directly translates to:
* No rate limits, you can easily scrape 50 thousand tweets in an hour (without even using threads!)
* No authentication is needed (the request header is random so you should'nt get blacklisted)
* And most importantly, you are free to query tweets that are more than 7 days old

This project is similar in nature to [taspinar's twitterscraper](https://github.com/taspinar/twitterscraper)
and was heavily inspired by it. In fact, a small portion of the code was shamelessly borrowed. 

The main difference between our two libraries is that this one is fully asynchronous so requests 
are non-blocking. This allows multiple requests to be processed in a shorter period of time, making 
the scraper much faster.

## Getting Started

Unfortunately, at the moment this package is only for python 3.6+ as it relies on newer features. 

### Installing

To install this package simply run

```
(sudo) pip install Twper
```

Or you can clone the repository and in the folder containing setup.py run

```
python setup.py install
```

### Examples

Each tweet is represented as a Tweet object and contains the following attributes:
* user - the sender's username
* fullname - the sender's full name
* tweet_id - a unique id (provided by twitter)
* url - a url to that specific tweet
* timestamp - a datetime object of when the tweet was sent
* text - the tweet's message
* replies - number of replies the tweet got
* retweets - number of retweets it got
* likes - number of likes the tweet received
* hashtags - what hashtags are mentioned in the tweet

*Note:* Tweet has a from_id constructor that returns a tweet object from a tweet_id. 

*Warning:* This feature uses requests and is blocking. 

To get additional info about a specific user you can use the TwitterAccount class. Specifically 
TwitterAccount.from_username(user) can be used. A TwitterAccount has the following attributes:
* user - the sender's username
* fullname - the sender's full name
* tweets - number of tweets the user tweeted
* following - number of people the user is following 
* followers - number of people following the user 
* likes - number of likes issued by the user
* lists - number of lists issued by the user
* moments - number of moments the user has
* bio - the user's biography (short description)
* location - the user's geographical location
* location_id - the corresponding location id twitter uses
* website - the user's website 
* birthday - datetime of the user's birthday if publicly available 
* joined - datetime of when the user joined

*Note:* Some of the above info might be missing/not publicly available. In this case the default value 
for dates is None, from strings it's an empty string and for ints its zero.

*Warning:* The from_username feature uses requests and is blocking. 

A search is described by a query string (q_str) and these have the following properties:

| q_str             | What it will query for                   |
|:-----------------:|:----------------------------------------:|
| A B C             | tweets containing A and B and C          |
|"ABC"              | tweets containing the exact match ABC    |
| A OR C            | tweets containing either A or C          |
| -A -B             | tweets NOT containing A and NOT B        |
| \#ABC             | tweets containing the hashtag \#ABC      |
| from:A            | tweets that are from account A           |
| to:B              | tweets that are to account B             |
| @C                | tweets that mention account C            |
| since:2017-12-01  | tweets after date                        |
| until:2017-12-02  | tweets before date                       |
| place:LOCATION_ID | tweets from location with id LOCATION_ID |


*Note:* Ordering does not matter, and a search is case-insensitive except for keywords OR, from:, to: 
since:, until: and place: which should be written exactly as above. Also there should NOT be a space 
between the colon and search value (ex: from: A is wrong and will search for tweets containing 
'from:' and 'A' instead of the intended behavior). 


In this package there's two classes used to search tweets (Query, Queries). Both these classes 
have a get_tweets method which returns an async generator. And therefore they need to be ran 
in an event loop. Do not worry if you haven't used these before, let's jump right into it!

```
async def main():
    # Example 1: A simple search using Query
    q = Query('Some Query Goes Here', limit=20)
    async for tw in q.get_tweets():
        # Process data
        print(tw)


# This actually runs the main function
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
    loop.run_until_complete(loop.shutdown_asyncgens())
finally:
    loop.close()
```

This will print the most recent 20 tweets (from newest to oldest) containing the words 
'some' and 'query' and 'goes' and 'here'. 

Sometimes, the q_str you want to query for is too long and it needs to be broken up into 
smaller pieces and ORed together. For this you can use the Queries class. The Queries class 
executes many different queries together and then joins them. In the following example four 
separate queries are executed at once and tweets are printed reverse chronological order 
(newest first). Please note that in the following Queries example is not faster than running 
those four queries sequentially, rather it merges them chronologically.

```
async def main():
    # Example 2: Multiple searches using Queries.
    qs = Queries(['Some', 'Query', 'Goes', 'Here'], limit=5)
    async for tw in qs.get_tweets():
        # Process data
        print(tw)


# This actually runs the main function
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
    loop.run_until_complete(loop.shutdown_asyncgens())
finally:
    loop.close()
```

The limit key word argument simply limits the maximum number of results any generator can yield. 
In the second example the limit is applied to every query individually so the maximum  number of 
tweets it can yield is 5 x 4 = 20.

For further question I encourage you to look at the source code as it is not long and well 
commented before asking. 

## Contributing

This is my first open source project, so please feel free to contribute in any way and/or point 
out what I should improve (as well as any bugs of course). Pull requests and issues are welcomed.

## Todo

If you are looking to contribute or just curious about what I plan to add/fix here is the todo list:

* Remove the requests dependency. This is a blocking library that should be replaced by aiohttp. It 
is only used in Tweet.from_id and TwitterAccount.from_username and therefore doesn't affect the 
performance of Querying.

* Improve the TwitterAccount class. Hopefully it's possible to scrape what accounts a user 
is following and what accounts are following the user if we add authentication. Currently we can 
only retrieve stats about a user account.

* Possibly add support for other languages. Currently, only english is fully supported even though 
you can set language to something other than 'en' in the Query constructor. Setting it to None searches 
everything regardless of the language.

## Authors

* Sacha Jungerman - Initial Work - [Twper](https://github.com/jungerm2/Twper)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) for details

## Acknowledgments

* Credit's to [Taspinar](http://www.ataspinar.com) for his great library that inspired the 
creation of this one.