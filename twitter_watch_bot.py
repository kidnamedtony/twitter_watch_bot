import pandas as pd
import numpy as np
import sys
import string
import os
import re
from fuzzywuzzy import fuzz
import json
import logging
from dotenv import load_dotenv
import tweepy
from twilio.rest import Client

# Set up logger configuration
logging.basicConfig(
    filename="bot_log.log"
    , filemode="a"
    , level=logging.INFO
    , format="%(asctime)s %(name)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s"
    , datefmt="%Y-%m-%d %H:%M:%S")

# Create new logger object
logger = logging.getLogger("bot_logger")
# Create and configure our handler objects (they take info from log objects, which contains all the info we want in a log entry, and tell that info where to go)
console_handler = logging.StreamHandler(sys.stdout) # this outputs to stdout
file_handler = logging.FileHandler("bot_log.log") # this outputs to our logfile
# Set logging level for our handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)
# Set format for our handler objects
console_format = logging.Formatter("%(name)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s")
file_format = logging.Formatter("%(asctime)s %(name)s - %(levelname)s - %(module)s - %(funcName)s: %(message)s")
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)
# Add our modified handler objects to the logger object
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# Test messages
logging.debug("Test debug message")
logging.info("Test info message")
logging.warning("Test warning message")
logging.error("Test error message")
logging.critical("Test critical message")

# load API credentials via environment variables w/dotenv
load_dotenv("env_vars.env", verbose=True)

# set credential variables and authenticate w/Twitter
twitter_api_key = os.environ.get("TWITTER_API_KEY")
twitter_api_secret = os.environ.get("TWITTER_API_SECRET")
twitter_access_key = os.environ.get("TWITTER_ACCESS_KEY")
twitter_access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_access_key, twitter_access_secret)

# Create Twitter API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

# If our API works, we should get an authenication confirmation message
try:
    api.verify_credentials()
    logging.info("Twitter API credentials authenticated")
    print("Twitter API credentials authenticated")
except:
    logging.info("Error during Twitter API credentials authentication")
    print("Error during Twitter API credentials authentication")

# Setting Twilio variables and Client for SMS notification
twilio_acctSID = os.environ.get("TWILIO_ACCTSID")
twilio_authToken = os.environ.get("TWILIO_AUTHTOKEN")
twilio_client = Client(twilio_acctSID, twilio_authToken)
myTwilioNumber = os.environ.get("MYTWILIONUMBER")
cell_0 = os.environ.get("CELL_0")
cell_1 = os.environ.get("CELL_1")
logging.info(f"Check cell #s loaded: {len(cell_0)!=0}, {len(cell_1)!=0}")
print(f"Check cell #s loaded: {len(cell_0)!=0}, {len(cell_1)!=0}")

# Fetching Twitter IDs for users we want to watch
twitter_id_0 = os.environ.get("TWITTER_ID_0")
twitter_id_1 = os.environ.get("TWITTER_ID_1")
twitter_id_lst = [twitter_id_0, twitter_id_1]
logging.info(f"Check Twitter IDs loaded: {twitter_id_lst}")
print(f"Check Twitter IDs loaded: {twitter_id_lst}")

# list to hold the strings we want to watch for, all set to lower case
from vars import watch_lst
# watch_lst = os.environ.get("WATCH_LST").split(",")
watch_lst = [watchword.lower() for watchword in watch_lst]
logging.info(f"Watchword list: {watch_lst}")
print("Watchword list:", watch_lst)

# Helper functions for our StreamListener class

def from_followed_usr(tweet):
    """
    Function to filter tweets to ONLY the users we're watching (otherwise we'll get RTs to or
    replies mentioning the users we're watching just because their user IDs in these tweets by
    other users. W/out filtering, it opens up a firehose of tweets we don't need deal with).

    INPUT:
    - tweet: "tweet" or "status" object from tweepy, which contains all information about a
    user's current status (tweet text, tweet ID, user ID, RT status, etc.)

    OUTPUT:
    - boolean: a boolean value that basically tells our StreamListener class whether to process
    a tweet or not in its on_status() function
    """
    if str(tweet.user.id) not in twitter_id_lst:
        return False
    else:
        return True

# Notification function to call if notification requirements are met
def send_notification(tweet, notification_type):
    """
    Function that sends a notification if required conditions are met in StreamListener's
    on_status() function

    INPUT:
    - tweet: "tweet" or "status" object from tweepy, which contains all information about a
    user's current status (tweet text, tweet ID, user ID, RT status, etc.)
    - notification_type: list; list containing the various notifications that a given tweet/
    status-update has fulfilled in StreamListener's on_status() function

    OUTPUT:
    No returns, however function should print the tweet and its notification type(s) that
    it's given as arguments, and will send text notifications via the Twilio REST client to
    the specified recipients
    """
    notification_type = "".join(notification_type)
    # Print locally
    logging.info(f"notification type: {notification_type}\n{tweet.user.name}: {tweet.text}\n")
    print(f"notification type: {notification_type}\n{tweet.user.name}: {tweet.text}\n")
    # Send notifications
    notify_0 = twilio_client.messages.create(body=f"type: {notification_type}\t{tweet.user.name}:{tweet.text}"
                        , from_=myTwilioNumber, to=cell_0)
    notify_1 = twilio_client.messages.create(body=f"type: {notification_type}\t{tweet.user.name}:{tweet.text}"
                        , from_=myTwilioNumber, to=cell_1)

def cleanup_tweet(tweet):
    """
    Function to take tweepy status/tweet object and remove punctuation, then split tweet text
    into individual words contained in a list

    INPUT:
    - tweet: "tweet" or "status" object from tweepy, which contains all information about a
    user's current status (tweet text, tweet ID, user ID, RT status, etc.)

    OUTPUT:
    - cleaned_tweet_lst: list; list containing the individual word strings of the tweet's text,
    sans punctuation
    """
    # This line removes common punctuation, but doesn't split words on spaces
    common_punct_removed = re.split("[?!.,]", tweet.text)
    # These next 2 lines rejoin our list of strings together before splitting them on spaces instead
    tweet_rejoined = " ".join(common_punct_removed)
    common_punct_removed = tweet_rejoined.split()
    # Setting up empty list for output
    cleaned_tweet_lst = []
    # This for loop removes less common punctuation (may be refined or removed in future)
    for word in common_punct_removed:
        word = word.translate(word.maketrans("","",string.punctuation))
        cleaned_tweet_lst.append(word)
    return cleaned_tweet_lst

def find_exact_match(cleaned_tweet_lst, notification_type):
    """
    Function that counts the instances of exact matches between the words in a given tweet
    and the words in our watch list

    INPUT:
    - cleaned_tweet_lst: list; list containing the individual word strings of the tweet's text,
    sans punctuation
    - notification_type: list; list containing the various notifications that a given tweet/
    status-update has fulfilled in StreamListener's on_status() function

    OUTPUT:
    - match: int; the number of matches between the given tweet's text and the words in our watch list
    - notification_type: list; this function should append "EXACT MATCH; " to notification_type
    should there be at least one exact match between the given tweet's text and the words in our
    watch list. Otherwise, no notification message will be appended
    """
    match = 0
    for word in cleaned_tweet_lst:
        word = word.lower()
        if word in watch_lst:
            match+=1
    if match>=1:
        notification_type.append("EXACT MATCH; ")
    return match, notification_type

def count_words_in_tweet(cleaned_tweet_lst, notification_type):
    """
    Function that counts the instances of exact matches between the words in a given tweet
    and the words in our watch list

    INPUT:
    - cleaned_tweet_lst: list; list containing the individual word strings of the tweet's text,
    sans punctuation
    - notification_type: list; list containing the various notifications that a given tweet/
    status-update has fulfilled in StreamListener's on_status() function

    OUTPUT:
    - words_in_tweet: int; the number of words in a given tweet (or more specifically, the number
    of word strings there are in a tweet's cleaned_tweet_lst list as generated by the
    cleanup_tweet() function)
    - notification_type: list; this function should append "1-WORD TWEET; " to notification_type
    should the tweet only be one word in length. Otherwise, no notification message will be
    appended
    """
    words_in_tweet = len(cleaned_tweet_lst)
    if words_in_tweet==1:
        notification_type.append("1-WORD TWEET; ")
    return words_in_tweet, notification_type

def get_fuzzy_matches(cleaned_tweet_lst, notification_type):
    """
    Function to generate fuzzy match ratios for each word in a given tweet, and the words in our
    watch list before returning the terms with the highest match ratio.

    INPUT:
    - cleaned_tweet_lst: list; list containing the individual word strings of the tweet's text,
    sans punctuation
    - notification_type: list; list containing the various notifications that a given tweet/
    status-update has fulfilled in StreamListener's on_status() function

    OUTPUT:
    - MAXFuzzy_word: string; the word pair with the highest fuzzy word ratio
    - MAXFuzzy_score: float; float value of the highest fuzzy word ratio
    - notification_type: list; this function should append f"FUZZY MATCH [{MAXFuzzy_word} |
    {MAXFuzzy_score}]" to notification_type should there be at least one word pair that has
    a fuzzy match ratio of 70 or higher. Otherwise, no notification message will be appended
    """
    # create DF with each (watchword | word in tweet)'s fuzzy match score
    watch_df = pd.DataFrame()
    for word in cleaned_tweet_lst:
        for watchword in watch_lst:
            current_score = fuzz.ratio(watchword, word.lower())
            # create new column w/ (watchword | tweet word) pair, insert fuzzy match score
            watch_df.loc[0, f'{watchword} | {word.lower()}'] = current_score
    # find greatest fuzzy match score in DF and the word pair it belongs to
    MAXFuzzy_word = watch_df.idxmax(axis=1).values[0]
    MAXFuzzy_score = watch_df.max(axis=1).values[0]
    if MAXFuzzy_score >= 70:
        notification_type.append(f"FUZZY MATCH [{MAXFuzzy_word} | {MAXFuzzy_score}]")
    return MAXFuzzy_word, MAXFuzzy_score, notification_type

# Create tweet stream listener class
class TweetListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        """
        Function that is fed tweet/status objects and runs other functions if certain conditions
        are met (e.g., if tweet is by those users we're following, if tweet text contains any
        term matches, contains a single word, etc.)
        """
        # Check if tweet is from one of the users we're following (i.e., not a RT or reply)
        if from_followed_usr(tweet):
            # notification variable set to 0, and notifcation type to None
            notification_type = []
            logging.info(f"START EVAL: User ID: {tweet.user.id} Tweet ID: {tweet.id}\nNT: {notification_type}, NT len: {len(notification_type)}")
            print(f"START EVAL: User ID: {tweet.user.id} Tweet ID: {tweet.id}\nNT: {notification_type}, NT len: {len(notification_type)}")

            # Split tweets into words, and remove punctuation
            cleaned_tweet_lst = cleanup_tweet(tweet)

            # If there's an exact match, send a text of the tweet
            match, notification_type = find_exact_match(cleaned_tweet_lst, notification_type)

            # If tweet is only one word long
            words_in_tweet, notification_type = count_words_in_tweet(cleaned_tweet_lst, notification_type)

            # else, if there's a term with a fuzzy match score of >= 70, send a text of the tweet
            MAXFuzzy_word, MAXFuzzy_score, notification_type = get_fuzzy_matches(cleaned_tweet_lst, notification_type)

            logging.info(f"END EVAL:\nNT: {notification_type}, Match: {match}, WIT: {words_in_tweet},\nMAXFuzzy_word: {MAXFuzzy_word}, MAXFuzzy_score: {MAXFuzzy_score}")
            print(f"END EVAL:\nNT: {notification_type}, Match: {match}, WIT: {words_in_tweet},\nMAXFuzzy_word: {MAXFuzzy_word}, MAXFuzzy_score: {MAXFuzzy_score}")

            if len(notification_type)>=1:
                send_notification(tweet, notification_type)

    def on_error(self, status, status_code):
        print("Error: check logs")
        if status_code==420:
            print("Error 420")
            return False

# set TweetListener class variable
tweet_listener = TweetListener(api)

# set tweet stream variable
stream = tweepy.Stream(api.auth, tweet_listener)

# tell stream variable who to follow and what to listen for
# the "follow" line assumes you'll want to follow your own Twitter account (for
# testing) and another Twitter account (for fun or [insert reason here])
stream.filter(follow=twitter_id_lst)
stream.filter(track=watch_lst, languages=["en"])
