from re import T
import requests, json, tweepy, logging, time

logging.basicConfig(level=logging.INFO)
with open('config.json',"r") as cfg:       #setup
    tmp = json.load(cfg)
    if len(tmp['apis']) != 0:
        api = tmp["apis"][0]               #base api key set for usage
    else:
        prompt = input("Do you want to add API keys? (y/n): ")          #code for adding more API keys
        if prompt == "y":
            while True:    
                api_key = input('API key: ')
                api_key_secret = input('API key secret: ')
                access_token = input('Access token: ')
                access_token_secret = input('Access token secret: ')
                if len(api_key) != 25 or len(api_key_secret) != 50 or len(access_token) != 50 or len(access_token_secret) != 45:
                    logging.error("Invalid length of one of the inputted parameters, please try again.")
                else:
                    tmp["apis"].append({
                        "api_key": api_key,
                        "api_key_secret": api_key_secret,
                        "access_token": access_token,
                        "access_token_secret": access_token_secret
                    })
                    prompt2 = input("Do you want to enter another one? (y/n): ").lower()
                    if prompt2 == "n":
                        break
        else:
            logging.error("This script won't work without API keys, please enter at least one.")
    if tmp["webhook"] == "":                                               #webhook retrieval
        webhook = input('Please enter a discord webhook URL: ')
        tmp["webhook"] = webhook
    else:
        webhook = tmp["webhook"]
    if tmp["monitored_user"] == "" or tmp["remember_user"] == "no":        #user monitoring input
        user = input('Please enter the @ of a user to monitor: ')
        tmp["monitored_user"] = user.lower()
        remember = input("Remember this user? Can be later changed in config.json. (y/n): ")
        if remember == "y":
            tmp["remember_user"] = "yes"
        else:
            tmp["remember_user"] = "no"
    with open("config.json", "w") as update:                               #save config
        json.dump(tmp, update)
    logging.info("Config successfully loaded")

logging.info(f"Started monitoring {tmp['monitored_user']}")

api_keys = tmp["apis"][0]
auth = tweepy.OAuthHandler(api_keys["api_key"], api_keys["api_key_secret"])
auth.set_access_token(api_keys["access_token"], api_keys["access_token_secret"])        #authenticate with the first api key set
api = tweepy.API(auth)


tl = api.user_timeline(screen_name = tmp["monitored_user"], count = 1, include_rts = False, tweet_mode = 'extended')[0]._json        #initial timeline pull
count = 0
time_init = time.time()
while True:
    time_loop_start = time.time()
    try:
        tl_new = api.user_timeline(screen_name = tmp["monitored_user"], count = 1, include_rts = False, tweet_mode = 'extended')[0]._json
        if tl_new["id"] != tl["id"]:
            username = tmp["monitored_user"]
            twitter_name = tl_new["user"]["name"]
            followers = tl_new["user"]["followers_count"]
            status_id = tl_new["id_str"]
            text = tl_new["full_text"]
            avatar_url = tl_new["user"]["profile_image_url"]
            embed = {
                'username': f"{username} Monitor",
                "avatar_url": avatar_url,
                "embeds": [
                    {
                        "author": {
                            "name": f"{twitter_name} (@{username} // {followers} followers)",
                            "url": f"https://twitter.com/{username}",
                        },
                        "title": "Link to Tweet",
                        "url": f"https://twitter.com/{username}/status/{status_id}",
                        "color": 2291967,
                        'description': text
                    }
                ]
            }
            if "media" in tl_new["entities"]:                                                                   #checks if an image exists
                embed["embeds"][0]["image"] = {"url": tl_new["entities"]["media"][0]["media_url_https"]}
            if len(tl_new["entities"]["user_mentions"]) > 0:                                                    #checks if any user is mentioned
                mentions = {"name":"Mentioned users", "value":""}
                for user in tl_new["entities"]["user_mentions"]:
                    mentions["value"] += f"[{user['name']}](https://twitter.com/{user['screen_name']}) "
                embed["embeds"][0]["fields"] = []
                embed["embeds"][0]["fields"].append(mentions)
            requests.post(webhook, json = embed)
            logging.info(f"Found a new post and posted it to discord.\nPOST ID: {status_id}")
            tl = tl_new
    except Exception as e:
        logging.error(f'Exception while fetching user tweet, callback: {e}')
        pass

    time_loop_end = time.time()
    time_master = time_loop_end - time_init
    time_diff = time_loop_end - time_loop_start
    sleep_time = (900 - time_master)/(898 - count) - time_diff
    if time_master >= 900 or count >= 897:
        time_init = time_loop_end
        count = 0
    if sleep_time >= 0:
        time.sleep(sleep_time)
    count += 1
