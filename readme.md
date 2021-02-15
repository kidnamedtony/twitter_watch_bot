# Twitter Watch Bot
Admittedly, it's not the wittiest of names, but it does convey what this Python script is designed to do!

### A Bit of Background:

At the recommendation/request of a friend who trades crypto currency, I made a simple Twitter bot in Python designed to watch the tweet stream of a very influential Twitter user (one who moves cryptocurrency markets with their tweets). If this influential user tweeted a message that was either a single word or contained terms that matched (either exactly or partially) a list of predefined "watch words", the bot would then send us an SMS notification. This way, my friend could afford to pay selective attention to tweets that might affect his portfolio; no more, no less.

I eventually decided that it would probably be best if I generalized the script so that anyone who wanted to use similar `watching-->match-->notification` functionality could feed it their own Twitter user IDs to follow as well as their own list of watch words. This more generalized version of the bot is what is contained in this repo.

### What You'll Need

Before getting started, you'll need:
- A Twitter developer account to gain access to the Twitter API. If you already have a Twitter account, or once you get one, you can apply for a dev account [here](https://developer.twitter.com/en/apply-for-access)
- A [Twilio account](https://www.twilio.com/messaging) to use their REST client for SMS notifications (**NOTE**: I may add in other notification methods such as email in future, but for now it's only SMS)

After that, you'll need the files in this repo:
- **env_vars.env:** an environment file that you'll paste a bunch of info into:
    - your Twitter API and secret keys
    - your Twilio account keys and auth token
    - the various phone numbers you'll be sending SMS texts to and from
    - and the numerical Twitter IDs of the Twitter users you want to follow
- **vars.py:** a simple .py script that contains a list of the terms you want Twitter Watch Bot to watch out for
- **twitter_watch_bot.py:** the Python script of the bot itself!

Regarding the `vars.py` and `env_vars.env` files mentioned above, this repository only contains templates of both. Be sure to alter them to fulfill your required specifications!

### Running Twitter Watch Bot

Once the necessary info has been copy-pasted into `env_vars.env` and `vars.py`, all Twitter Watch Bot needs to run is to have all its files copied to the same directory (e.g., `usr/local/twitter_watch_bot`)

Then, the script can be executed from a bash terminal (navigated to the directory where all three files are, e.g., `usr/local/twitter_watch_bot`) with `python3 twitter_watch_bot.py`, and will run until an error occurs or it's `ctrl-c` stopped by a user.

### Shoutouts

This is my first time building a Twitter bot, and as a result, I leaned on a lot of great internet resources! Sincerest thanks to:
- RealPython (and in particular, [Miguel Garcia's Tweepy tutorial](https://realpython.com/twitter-bot-python-tweepy/))
- Al Sweigart's [_Automate the Boring Stuff with Python_](https://automatetheboringstuff.com/)
- and of course, the communal coding wisdom of StackOverflow!
