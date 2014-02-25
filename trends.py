"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from doctest import run_docstring_examples
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait, message
from string import ascii_letters
from ucb import main, trace, interact, log_current_line
from functools import reduce
from operator import add


# Phase 1: The Feelings in Tweets

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as a python dictionary.

    text      -- A string; the text of the tweet, all in lowercase
    time      -- A datetime object; the time that the tweet was posted
    latitude  -- A number; the latitude of the tweet's location
    longitude -- A number; the longitude of the tweet's location

    >>> t = make_tweet("Just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_words(t)
    ['Just', 'ate', 'lunch']
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    """
    return {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}

def tweet_words(tweet):
    """Return a list of the words in the text of a tweet."""
    "*** YOUR CODE HERE ***"
    return extract_words(tweet['text'])

def tweet_time(tweet):
    """Return the datetime that represents when the tweet was posted."""
    "*** YOUR CODE HERE ***"
    return tweet['time']

def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location."""
    "*** YOUR CODE HERE ***"
    return make_position(tweet['latitude'], tweet['longitude'])

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(tweet['text'], tweet_location(tweet))

def extract_words(text): #I did this in a brutal way... You see if there is a better way or not
    """Return the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    """
    "*** YOUR CODE HERE ***"
    split_text = (w for w in text) #Split text into characters
    def ascii_filter(w):
        if w in ascii_letters:
            return w
        else: 
            return ' '
    return reduce(add, (map(ascii_filter, split_text))).split()  

def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.

    >>> s = make_sentiment(0.2)
    >>> t = make_sentiment(None)
    >>> has_sentiment(s)
    True
    >>> has_sentiment(t)
    False
    >>> sentiment_value(s)
    0.2
    """
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    "*** YOUR CODE HERE ***"
    def dispatch(m):
        if m == 'has_sentiment': 
            return value != None
        elif m == 'sentiment_value':
            return value
        else:
            print('Not supported')
    return dispatch

def has_sentiment(s):
    """Return whether sentiment s has a value."""
    "*** YOUR CODE HERE ***"
    return s('has_sentiment')

def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    "*** YOUR CODE HERE ***"
    return s('sentiment_value')

def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word, if word is not in the sentiment dictionary.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    return make_sentiment(word_sentiments.get(word, None))

def analyze_tweet_sentiment(tweet):
    """ Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    average = make_sentiment(None)
    "*** YOUR CODE HERE ***" 
    if tweet_words(tweet) == None: 
        return average
    total, count = 0, 0
    #print("This is working here")
    #print("all words: ", tweet_words(tweet))
    for w in tweet_words(tweet):
        #print("This is working")
        #print(w)
        if has_sentiment(get_word_sentiment(w)):
            total += sentiment_value(get_word_sentiment(w))
            count += 1
    if count == 0:
        return make_sentiment(None)
    return make_sentiment(total / count)


# Phase 2: The Geometry of Maps

#From Lecture
def summation(n, term, next):
    total, k = 0, 0
    while k < n:
        total, k = total + term(k), next(k)
    return total

def successor(k):
    return k + 1
    
def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p3, p2, p1])
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p2, p1])
    (1, 2, 0)
    """
    "*** YOUR CODE HERE ***"
    x, y = [], []
    for p in polygon: 
        x += [latitude(p)]
        y += [longitude(p)]
    n = len(x)
    #print("x: ", x, "\ny: ", y)
    def area_term(i):
        #print('x[i]: ', x[i])
        #print('y[i + 1]: ', y[i + 1])
        #print('x[i] * y[i + 1]: ', x[i] * y[i + 1])
        #print('x[i] * y[i + 1] - x[x + 1] * y[i]: ',  x[i] * y[i + 1] - x[x + 1] * y[i])
        #print(i)
        return x[i] * y[i + 1] - x[i + 1] * y[i]
    area = .5 * summation(n - 1, area_term, successor)
    # If a polygon has 0 area, return its first position as its centroid
    if area == 0: 
        return (x[0], y[0], 0)
    def cx_term(i): 
        return (x[i] + x[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
    def cy_term(i): 
        return (y[i] + y[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
    cx = (1/(6 * area)) * summation(n - 1, cx_term, successor)
    cy = (1/(6 * area)) * summation(n - 1, cy_term, successor)
    area = abs(area)
    return (cx, cy, area)
    
def get_cx(centroid):
    return centroid[0]
def get_cy(centroid):
    return centroid[1]
def get_area(centroid):
    return centroid[2]

def find_center(polygons):
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    "*** YOUR CODE HERE ***"
    n = len(polygons) #Number of islands
    if n == 1:
        centroid = find_centroid(polygons[0])
        return make_position(get_cx(centroid), get_cy(centroid))
    cx, cy, area = [], [], []
    for p in polygons:
        centroid = find_centroid(p)
        cx.append(get_cx(centroid))
        cy.append(get_cy(centroid))
        area.append(get_area(centroid))
    def numer_term(coor):
        def numer(i):
            return coor[i] * area[i]
        return numer
    def denom_term(coor):
        def denom(i):
            return area[i]
        return denom
    x = summation(n, numer_term(cx), successor) / summation(n, denom_term(cx), successor)
    y = summation(n, numer_term(cy), successor) / summation(n, denom_term(cy), successor)
    return make_position(x, y)

# Phase 3: The Mood of the Nation

def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.

    Use the geo_distance function (already provided) to calculate distance
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a dictionary from state names to positions.

    >>> us_centers = {n: find_center(s) for n, s in us_states.items()}
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    "*** YOUR CODE HERE ***"
    loc = tweet_location(tweet)
    closest_state = 'CA' #initialize to CA
    min_dist = geo_distance(state_centers['CA'], loc)
    for state in state_centers:
        dist = geo_distance(state_centers[state], loc)
        if dist < min_dist:
            closest_state = state
            min_dist = dist
    return closest_state
        
#not really sure if it works of not because the test case was too simple
def group_tweets_by_state(tweets):
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> ca_tweets = group_tweets_by_state([sf, ny])['CA']
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
    tweets_by_state = {}
    "*** YOUR CODE HERE ***"
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    for tweet in tweets: 
        state = find_closest_state(tweet, us_centers)
        if tweets_by_state.get(state, -1) == -1: 
            tweets_by_state[state] = [tweet]
        tweets_by_state[state].append(tweet)
    return tweets_by_state

def most_talkative_state(term):
    """Return the state that has the largest number of tweets containing term.

    >>> most_talkative_state('texas')
    'TX'
    >>> most_talkative_state('sandwich')
    'NJ'
    """
    tweets = load_tweets(make_tweet, term)  # A list of tweets containing term
    "*** YOUR CODE HERE ***"
    tweets_by_state = group_tweets_by_state(tweets)
    talkative = 'HI'
    max_tweet = len(tweets_by_state['HI'])
    #print('CA num:', len(tweets_by_state['CA']))
    for state in tweets_by_state:
        state_num = len(tweets_by_state[state])
        if state_num >= max_tweet: 
            talkative = state
            max_tweet = state_num
            #print('max: ', max_tweet, 'name: ', state)
    return talkative

def average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
    """
    #Test Case: average_sentiments({'CA': 
    averaged_state_sentiments = {}
    "*** YOUR CODE HERE ***"
    for state in tweets_by_state: 
        total = total_sentiments(tweets_by_state[state])
        if total[1] != 0: #Abstraction can be improved
            averaged_state_sentiments[state] = total[0] / total[1]
    #print('avg_state_sentiments:', averaged_state_sentiments)
    return averaged_state_sentiments

def total_sentiments(tweets): 
    """Return 2 numbers: 1. Total of sentiments of a state; 2. Number of tweets with sentiments
    """
    total = 0
    n = 0
    for tweet in tweets:
        sentiment = analyze_tweet_sentiment(tweet)
        if has_sentiment(sentiment) == True: 
            total += sentiment_value(sentiment)
            n += 1
    return (total, n)

# Phase 4: Into the Fourth Dimension

def group_tweets_by_hour(tweets):
    """Return a dictionary that groups tweets by the hour they were posted.

    The keys of the returned dictionary are the integers 0 through 23.

    The values are lists of tweets, where tweets_by_hour[i] is the list of all
    tweets that were posted between hour i and hour i + 1. Hour 0 refers to
    midnight, while hour 23 refers to 11:00PM.

    To get started, read the Python Library documentation for datetime objects:
    http://docs.python.org/py3k/library/datetime.html#datetime.datetime

    tweets -- A list of tweets to be grouped
    """
    tweets_by_hour = {}
    "*** YOUR CODE HERE ***"
    for hr in range(24): #Create keys for every hour
        tweets_by_hour[hr] = []
    for tweet in tweets: 
        tweets_by_hour[tweet_time(tweet).hour].append(tweet)
        #print('tweet_time: ', tweet_time(tweet).hour)
        #print(tweet)
    #print('returning: ', tweets_by_hour)
    return tweets_by_hour


# Interaction.  You don't need to read this section of the program.

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in extract_words(text.lower()):
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments={}):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def draw_map_by_hour(term='my job', pause=0.5):
    """Draw the sentiment map for tweets that match term, for each hour."""
    tweets = load_tweets(make_tweet, term)
    tweets_by_hour = group_tweets_by_hour(tweets)

    for hour in range(24):
        current_tweets = tweets_by_hour.get(hour, [])
        tweets_by_state = group_tweets_by_state(current_tweets)
        state_sentiments = average_sentiments(tweets_by_state)
        draw_state_sentiments(state_sentiments)
        message("{0:02}:00-{0:02}:59".format(hour))
        wait(pause)

def run_doctests(names):
    """Run verbose doctests for all functions in space-separated names."""
    g = globals()
    errors = []
    for name in names.split():
        if name not in g:
            print("No function named " + name)
        else:
            if run_docstring_examples(g[name], g, True) is not None:
                errors.append(name)
    if len(errors) == 0:
        print("Test passed.")
    else:
        print("Error(s) found in: " + ', '.join(errors))

@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--run_doctests', '-t', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_term', '-m', action='store_true')
    parser.add_argument('--draw_map_by_hour', '-b', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))

