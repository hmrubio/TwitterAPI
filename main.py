import os
import sys
from datetime import datetime
from TwitterAPI import (
    TwitterAPI,
    TwitterOAuth,
    TwitterRequestError,
    TwitterConnectionError,
    HydrateType,
    OAuthType,
)
import json

def stream_tweets(query, expansions, tweet_fields, user_fields):

    datetimestart = datetime
    try:
        o = TwitterOAuth.read_file()
        api = TwitterAPI(
            o.consumer_key,
            o.consumer_secret,
            auth_type=OAuthType.OAUTH2,
            api_version="2",
        )

        # DELETE STREAM RULES
        r = api.request("tweets/search/stream/rules", method_override="GET")
        rules = r.json()
        if "data" in rules:
            ids = list(map(lambda rule: rule["id"], rules["data"]))
            api.request("tweets/search/stream/rules", {"delete": {"ids": ids}})

        # ADD STREAM RULES
        r = api.request("tweets/search/stream/rules", {"add": [{"value": query}]})
        print(f"[{r.status_code}] RULE ADDED: {json.dumps(r.json(), indent=2)}\n")
        if r.status_code != 201:
            exit()

        # GET STREAM RULES

        r = api.request("tweets/search/stream/rules", method_override="GET")
        print(f"[{r.status_code}] RULES: {json.dumps(r.json(), indent=2)}\n")
        if r.status_code != 200:
            exit()

        # START STREAM

        r = api.request(
            "tweets/search/stream",
            {
                "expansions": expansions,
                "tweet.fields": tweet_fields,
                "user.fields": user_fields,
            },
            hydrate_type=HydrateType.APPEND,
        )

        if r.status_code != 200:
            exit()
        
        if not os.path.exists("data.json"):
            open("data.json", "x", encoding="utf-8")

        with open("data.json", "r+", encoding="utf-8") as file:
            cantidad_tweets = len(file.readlines())
            file.seek(0, os.SEEK_END)

            print("------------------------------------------------------------")
            datetimestart = datetime.now()
            print(
                (
                    "Proceso de recopilación iniciado: "
                    + datetimestart.strftime("%d/%m/%Y %H:%M:%S")
                )
            )

            for item in r:
                json.dump(item, file, ensure_ascii=False, indent=None)
                file.write("\n")

                cantidad_tweets += 1
                sys.stdout.write(
                    f"\rTamaño actual del archivo: {file.tell() / 1000} kb | Cantidad de tweets: {cantidad_tweets}"
                )

    except KeyboardInterrupt:
        datetimeend = datetime.now()
        print("\nProceso terminado: " + datetimeend.strftime("%d/%m/%Y %H:%M:%S"))
        datetimeend = datetimeend - datetimestart
        print("Duración de la prueba " + (str(datetimeend)) + " horas/minutos/segundos")
        print("------------------------------------------------------------")

    except TwitterRequestError as e:
        print(f"\n{e.status_code}")
        for msg in iter(e):
            print(msg)
    except TwitterConnectionError as e:
        print(e)
    except Exception as e:
        print(e)

QUERY = "cambio climático OR sequías OR calentamiento global OR economía circular OR espacios verde OR protección ambiental lang:es -is:retweet"
EXPANSIONS = "author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username"
TWEET_FIELDS = "author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text"
USER_FIELDS = "created_at,description,entities,location,name,profile_image_url,public_metrics,url,username"

r = stream_tweets(QUERY, EXPANSIONS, TWEET_FIELDS, USER_FIELDS)