from datetime import datetime
from bs4 import BeautifulSoup
from coala_utils.decorators import generate_ordering
import random
import aiohttp
import asyncio
from fake_useragent import UserAgent
import requests

ua = UserAgent()
HEADERS_LIST = [ua.chrome, ua.google, ua['google chrome'], ua.firefox, ua.ff]


# For the most part this was shamelessly stolen from https://github.com/taspinar/twitterscraper
# All credits goes to 'taspinar' for this code and inspiring me to make this project
@generate_ordering('timestamp', 'tweet_id')
class Tweet(object):
    def __init__(self, user, fullname, tweet_id, url, timestamp, text, replies, retweets, likes):
        self.user = user
        self.fullname = fullname
        self.tweet_id = tweet_id
        self.url = url
        self.timestamp = timestamp
        self.text = text
        self.replies = replies
        self.retweets = retweets
        self.likes = likes
        self.hashtags = [tag for tag in self.text.split() if tag[0] == '#']

    def __repr__(self):
        return 'Tweet from {} on {}'.format(self.user, self.timestamp.strftime("%Y-%m-%d"))

    @classmethod
    def from_soup(cls, tweet):
        try:
            link = tweet.find('div', 'tweet')['data-permalink-path']
        except (KeyError, TypeError):
            link = tweet['data-permalink-path']
        return cls(
            user=tweet.find('span', 'username').text[1:],
            fullname=tweet.find('strong', 'fullname').text,
            tweet_id=tweet['data-item-id'],
            url=link,
            timestamp=datetime.utcfromtimestamp(
                int(tweet.find('span', '_timestamp')['data-time'])),
            text=tweet.find('p', 'tweet-text').text or "",
            replies=tweet.find(
                'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            retweets=tweet.find(
                'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
            likes=tweet.find(
                'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0',
        )

    @classmethod
    def from_html(cls, html):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('li', 'js-stream-item')
        if tweets:
            for tweet in tweets:
                try:
                    yield cls.from_soup(tweet)
                except AttributeError:
                    pass  # Incomplete info? Discard!

    # This is using requests, but it'll be nice to make it use aiohttp so it can
    # be async and get ids (plural) instead of just one at a time
    @classmethod
    def from_id(cls, tweet_id):
        url = 'https://twitter.com/anyuser/status/{}'.format(tweet_id)
        html = requests.get(url).text
        soup = BeautifulSoup(html, "lxml")
        tweet = soup.find('div', 'permalink-tweet')
        return cls.from_soup(tweet)


class TwitterAccount(object):

    def __init__(self, user, fullname, tweets, following, followers, likes, lists, moments, bio, location,
                 location_id, website, birthday, joined):
        self.user = user
        self.fullname = fullname
        self.tweets = tweets
        self.following = following
        self.followers = followers
        self.likes = likes
        self.lists = lists
        self.moments = moments
        self.bio = bio
        self.location = location
        self.location_id = location_id
        self.website = website
        self.birthday = birthday
        self.joined = joined

    def __repr__(self):
        return '{} @{}'.format(self.fullname, self.user)

    @classmethod
    def from_soup(cls, profile):
        def find_safe(soup, *args):
            if soup:
                return soup.find(*args)
            else:
                return None
        header = profile.find('div', 'ProfileHeaderCard')
        navbar = profile.find('div', 'ProfileCanopy-navBar')
        tws = find_safe(navbar.find('a', attrs={'data-nav': 'tweets'}), 'span', 'ProfileNav-value')
        fli = find_safe(navbar.find('a', attrs={'data-nav': 'following'}), 'span', 'ProfileNav-value')
        fle = find_safe(navbar.find('a', attrs={'data-nav': 'followers'}), 'span', 'ProfileNav-value')
        lks = find_safe(navbar.find('a', attrs={'data-nav': 'favorites'}), 'span', 'ProfileNav-value')
        lis = find_safe(navbar.find('a', attrs={'data-nav': 'all_lists'}), 'span', 'ProfileNav-value')
        mts = find_safe(navbar.find('a', attrs={'data-nav': 'user_moments'}), 'span', 'ProfileNav-value')
        loc = find_safe(header.find('div', 'ProfileHeaderCard-location'), 'a')
        wbs = find_safe(header.find('div', 'ProfileHeaderCard-url'), 'a')
        bdy = find_safe(header.find('div', 'ProfileHeaderCard-birthdate'), 'span', 'ProfileHeaderCard-birthdateText')
        jnd = find_safe(header.find('div', 'ProfileHeaderCard-joinDate'), 'span', 'ProfileHeaderCard-joinDateText')
        bdy = bdy if bdy.text.strip() else None
        jnd = jnd if jnd.text.strip() else None
        return cls(
            user=header.find('span', 'username').text[1:],
            fullname=header.find('a', 'ProfileHeaderCard-nameLink').text,
            tweets=int(tws['data-count']) if tws else 0,
            following=int(fli['data-count']) if fli else 0,
            followers=int(fle['data-count']) if fle else 0,
            likes=int(lks['data-count']) if lks else 0,
            lists=int(lis.text) if lis else 0,
            moments=int(mts.text) if mts else 0,
            bio=header.find('p', 'ProfileHeaderCard-bio').text or '',
            location=loc.text if loc else '',
            location_id=loc['data-place-id'] if loc else '',
            website=wbs['title'] if wbs else '',
            birthday=datetime.strptime(bdy.text.strip(), 'Born in %Y') if bdy else None,
            joined=datetime.strptime(jnd['title'].strip(), '%I:%M %p - %d %b %Y') if not jnd else None,
        )

    @classmethod
    def from_html(cls, html):
        profile = BeautifulSoup(html, "lxml")
        return cls.from_soup(profile)

    @classmethod
    def from_username(cls, username):
        url = 'https://twitter.com/{}'.format(username)
        html = requests.get(url).text
        return cls.from_html(html)


class Query(object):
    INIT_URL = "https://twitter.com/search?f=tweets&vertical=default&q={q}"
    RELOAD_URL = "https://twitter.com/i/search/timeline?f=tweets&vertical=" \
                 "default&include_available_features=1&include_entities=1&" \
                 "reset_error_state=false&src=typd&max_position={pos}&q={q}"

    def __init__(self, q_str, limit=20, language='en', sem=None):
        # Spaces are AND, or is OR. Also ordering does not matter
        # A B C     tweets containing A and B and C
        # "ABC"     tweets containing the exact match ABC
        # A OR C    tweets containing either A or C
        # -A -B:    tweets NOT containing A and NOT B
        # #ABC:     tweets containing the hashtag #ABC
        # from:A    tweets that are from account A (max: 47)
        # to:B      tweets that are to account B
        # @C        tweets that mention account C
        # since:2017-12-01  tweets after date
        # until:2017-12-02  tweets before date
        # place:LOCATION_ID tweets from location
        if language:
            self.INIT_URL += '&l={}'.format(language)
            self.RELOAD_URL += '&l={}'.format(language)
        if sem is None:
            sem = asyncio.Semaphore(10)
        if type(sem) is int:
            sem = asyncio.Semaphore(sem)
        self.sem = sem
        if not q_str or q_str.count('start:') > 1 or q_str.count('until:') > 1:
            raise ValueError('Invalid query')
        q_str = q_str.replace(' ', '%20').replace('#', '%23').replace('@', '%40').replace(':', '%3A')
        self.q_str = q_str
        self.limit = limit

    async def query_single_page(self, session, url, html_response=True, retry=3):
        headers = {'User-Agent': random.choice(HEADERS_LIST)}
        async with self.sem:
            async with session.get(url, headers=headers) as response:
                try:
                    if html_response:
                        html = await response.text()
                        tweets = list(Tweet.from_html(html))
                        if not tweets:
                            return [], None
                        return tweets, "TWEET-{}-{}".format(tweets[-1].tweet_id, tweets[0].tweet_id)
                    else:
                        json_resp = await response.json()
                        html = json_resp['items_html']
                        tweets = list(Tweet.from_html(html))
                        if not tweets:
                            return [], None
                        return tweets, json_resp['min_position']
                except (ConnectionError, aiohttp.client_exceptions):
                    if retry > 0:
                        return await self.query_single_page(session, url, html_response=html_response, retry=retry-1)
                return [], None

    async def get_tweets(self):
        pos = None
        num_tweets = 0
        async with aiohttp.ClientSession() as session:
            while True:
                new_tweets, pos = await self.query_single_page(
                    session,
                    self.INIT_URL.format(q=self.q_str) if pos is None
                    else self.RELOAD_URL.format(q=self.q_str, pos=pos),
                    html_response=(pos is None)
                )
                if len(new_tweets) == 0:
                    break
                for tw in new_tweets:
                    if num_tweets < self.limit or self.limit == 0:
                        yield tw
                        num_tweets += 1
                    else:
                        return


class Queries(object):

    def __init__(self, q_strs, limit=20, sem=None):
        if sem is None:
            sem = asyncio.Semaphore(10)
        if type(sem) is int:
            sem = asyncio.Semaphore(sem)
        self.sem = sem
        self.limit = limit
        self.q_strs = q_strs

    # This is an async generator that runs multiple queries at once it is not faster
    # than running queries sequentially but it merges them chronologically (newest first).
    # The limit kwargs is a the maximum number of elements that EACH
    # Query can return. Set to zero to search everything
    async def get_tweets(self):
        queries = [Query(q_str, limit=self.limit, sem=self.sem).get_tweets()
                   for q_str in self.q_strs]

        tweets, queries = await self.get_next_tweets(queries)
        while True:
            if not tweets:
                return
            else:
                max_tweet = max(tweets, key=self.unix_time)
                index = tweets.index(max_tweet)
                try:
                    tweets[index] = await queries[index].__anext__()
                except StopAsyncIteration:
                    tweets.remove(max_tweet)
                    del queries[index]
                yield max_tweet

    # Helper Method for the above function, it manually runs all generators
    # and removes any exhausted generators from the queries list
    @staticmethod
    async def get_next_tweets(queries):
        tweets = []
        filtered_qs = []
        for q in queries:
            try:
                tweets.append(await q.__anext__())
                filtered_qs.append(q)
            except StopAsyncIteration:
                pass
        return tweets, filtered_qs

    # This is a key function to sort tweets in chronologically
    @staticmethod
    def unix_time(t):
        return int(t.timestamp.timestamp()) if t else 0

