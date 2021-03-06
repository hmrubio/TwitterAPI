import os
import sys
import time
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
from diccionario_bloque_invertido import CreacionDeBloques

class BuscarTweets():
    QUERY = "cambio climático OR sequías OR calentamiento global OR economía circular OR espacios verde OR protección ambiental"
    EXPANSIONS = "author_id"
    TWEET_FIELDS = "created_at,text"
    USER_FIELDS = ""

    def __init__(self):
        self.stream_tweets(BuscarTweets.QUERY, BuscarTweets.EXPANSIONS, BuscarTweets.TWEET_FIELDS, BuscarTweets.USER_FIELDS)

    def stream_tweets(self, query, expansions, tweet_fields, user_fields):

        datetimestart = datetime
        try:
            o = TwitterOAuth.read_file("credentials.txt")
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
            print("Creando índice...")
            CreacionDeBloques("data.json", "./output")
            print("Índice creado con éxito.")

        except TwitterRequestError as e:
            print(f"\n{e.status_code}")
            for msg in iter(e):
                print(msg)
        except TwitterConnectionError as e:
            time.sleep(120)
            self.stream_tweets(BuscarTweets.QUERY, BuscarTweets.EXPANSIONS, BuscarTweets.TWEET_FIELDS, BuscarTweets.USER_FIELDS)
        except Exception as e:
            print(e)
            print("e")