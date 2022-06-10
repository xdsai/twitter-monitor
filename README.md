# Twitter user timeline monitor

This script monitors a user's timeline in real time and sends all new posts to a discord webhook via an embed. It uses Twitter's API, which you have to sign up for at [twitter's developer portal](http://developer.twitter.com)

## Setup

First clone the repository ->

```
git clone https://github.com/xdsai/twitter-monitor.git && cd twitter-monitor
```

Then install the required packages with pip ->

```
pip install -r requirements.txt
```

On first launch, you will be prompted to enter your API keys. These can be retrieved by making an app on twitter's developer portal, and copying the keys. You will also be prompted for a discord webhook url and the handle of the user you wish to monitor.

### Notes

There will be two modes available, a single-api key one, which has optimised sleep values to avoid rate limiting while checking for an update as often as possible - useful for when you don't need peak performance - this results in about 1 request a second, and a cyclic mode, which uses multiple API keys from multiple apps, that you have to create, to check for updates as often as possible. When one API key set gets rate limited, it is switched for another and the monitor will be resumed. This is so that there is no sleep needed between loops, and thus achieves better performance.

The main performance limiting factor of the cyclic mode is ping, where packets take a lot of time to get to Twitter's servers and back, therefore I recommend getting a server in San Francisco or similar. Discord server placement is a bit odd, but I have observed similar performance in all regions.

### CYCLIC MODE IS NOT IMPLEMENTED YET
