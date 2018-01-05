import asyncio
from datetime import datetime
from Twper import Query, Queries


async def main():
    total_tweets = 0
    # See Query for info on how to build a q_str
    q = Query('Some Query Goes Here', limit=20)
    async for tw in q.get_tweets():
        # Process data
        total_tweets += 1
        print(tw)

    print('------------------------------------------')

    qs = Queries(['Some', 'Query', 'Goes', 'Here'], limit=5)
    async for tw in qs.get_tweets():
        # Process data
        total_tweets += 1
        print(tw)
    return total_tweets

# This actually runs the main function
start = datetime.now()
loop = asyncio.get_event_loop()
try:
    total_tweets = loop.run_until_complete(main())
    loop.run_until_complete(loop.shutdown_asyncgens())
finally:
    loop.close()
elapsed = datetime.now() - start
print('\nThis example and fetched', total_tweets, 'in', elapsed)
print("That's an average of", elapsed.seconds/total_tweets, 'seconds per tweet fetched!')
