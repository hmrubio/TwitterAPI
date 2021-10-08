import os
import sys
from datetime import datetime
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, HydrateType, OAuthType
import json

QUERY = '"pizza" OR "hamburguesa"'
EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
TWEET_FIELDS='author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text'
USER_FIELDS='created_at,description,entities,location,name,profile_image_url,public_metrics,url,username'
def stream_tweets(query, expansions, tweet_fields, user_fields):
    
    try:
        o = TwitterOAuth.read_file()
        api = TwitterAPI(o.consumer_key, o.consumer_secret, auth_type=OAuthType.OAUTH2, api_version='2')

        # ADD STREAM RULES

        r = api.request('tweets/search/stream/rules', {'add': [{'value':QUERY}]})
        print(f'[{r.status_code}] RULE ADDED: {json.dumps(r.json(), indent=2)}\n')
        if r.status_code != 201: exit()

        # GET STREAM RULES

        r = api.request('tweets/search/stream/rules', method_override='GET')
        print(f'[{r.status_code}] RULES: {json.dumps(r.json(), indent=2)}\n')
        if r.status_code != 200: exit()

        # START STREAM

        r = api.request('tweets/search/stream', {
                'expansions': EXPANSIONS,
                'tweet.fields': TWEET_FIELDS,
                'user.fields': USER_FIELDS,
            },
            hydrate_type=HydrateType.APPEND)

        if r.status_code != 200: exit()
        with open('data.json', 'r+', encoding='utf-8') as file:
            cantidad_tweets = len(file.readlines())
            file.seek(0, os.SEEK_END)

            print("------------------------------------------------------------")
            print(f"Proceso de recopilación iniciado: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            for item in r:
                json.dump(item, file, ensure_ascii=False, indent=None)
                file.write('\n')

                cantidad_tweets += 1
                sys.stdout.write(f"\rTamaño actual del archivo: {file.tell() / 1000} kb | Cantidad de tweets: {cantidad_tweets}")

    except KeyboardInterrupt:
        print("\nProceso terminado: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("------------------------------------------------------------")

    except TwitterRequestError as e:
        print(f'\n{e.status_code}')
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)
    
QUERY = '"pizza" OR "burger"'
EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
TWEET_FIELDS='author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text'
USER_FIELDS='created_at,description,entities,location,name,profile_image_url,public_metrics,url,username'
r = stream_tweets(QUERY, EXPANSIONS, TWEET_FIELDS, USER_FIELDS)