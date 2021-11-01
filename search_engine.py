import datetime
from datetime import *
import json
from BTrees.OOBTree import OOBTree

from _ast import Break

def search_engine():
    print("\nBuscador de información recopilada...\
    \nIngrese la opción que desea utilizar.\
    \
    \n1.\tConsultas por fecha y hora.\
    \n2.\tConsultas de palabras o frases.\
    \n3.\tFinalizar.\
    \
    \n\nOpción número: ")
    
    while True:
        try: opcion_elegida = int(input())
        except ValueError: opcion_elegida = 0
        
        if (opcion_elegida == 1): consultas_por_fechahora(); break
        
        elif (opcion_elegida == 2): consultas_por_palabras(); break
            
        elif (opcion_elegida == 3): break
            
        else: print("Opción incorrecta. Ingrese nuevamente...")

def consultas_por_fechahora():
    print("\nIngrese los siguientes datos por favor...\
    \
    \ni.\tNombre de usuario (@por_ejemplo)\
        \n\t\tOpcional.*\
    \nii.\tCantidad de tuits (m primeros tuits)\
    \niii.\tFecha desde/hasta (dd/mm/aaaa - dd/mm/aaaa)\
        \n\t\tOpcional uno y/o el otro.*\
    \niv.\tHora desde/hasta (00:00 - 23:59)\
        \n\t\tOpcional uno y/o el otro.*")
    
    print("\nUsuario (@robertito sin @):"); nombre_usuario = input()
    print("\nCantidad de tuits:")
    while True:
        try: 
            cantidad_tuits = int(input())
            if cantidad_tuits <= 0: raise ValueError 
            break
        except ValueError: print("Ingrese cantidad de tuits válido...")
        
    print("\nFecha desde (dd/mm/aaaa hh:mm):")
    while True:
        try:
            fecha_desde = input()
            fecha_desde = datetime.strptime(fecha_desde, '%d/%m/%Y %H:%M') if fecha_desde else datetime.min; break
        except ValueError:
            print("Formato incorrecto en la fecha. Pruebe otra vez...")

    print("\nFecha hasta (dd/mm/aaaa hh:mm):")
    while True:
        try:
            fecha_hasta = input()
            fecha_hasta = datetime.strptime(fecha_hasta, '%d/%m/%Y %H:%M') if fecha_hasta else datetime.max;
            break
        except ValueError:
            print("Formato incorrecto en la fecha. Pruebe otra vez...")

    print("\nProcesando...")
    __obtener_tweets_por_fecha(nombre_usuario,cantidad_tuits,fecha_desde, fecha_hasta)

def consultas_por_palabras():
    print("\nIngrese los siguientes datos por favor...\
    \
    \ni.\tCantidad de tuits (m primeros tuits)\
    \nii.\tConsulta a realizar (por ejemplo: Adrián and Bussiness)\
        \n\t\tOpcional.*")
    
    print("\nCantidad de tuits:")
    while True:
        try: 
            cantidad_tuits = int(input())
            if cantidad_tuits <= 0: raise ValueError 
            break
        except ValueError: print("Ingrese cantidad de tuits válido...")
    
    print("\nIngrese su consulta (operadores permitidos OR, AND, NOT)...")
    while True:    
        text = input()
        query = text.split(" ") if len(text) > 0 else text
        if (len(query) != 0): break
        print("Debe ingresar una consulta...")

def procesar_archivo(*args):
    with open("data.json", "r", encoding = "utf-8") as file:
        for i in file:
            objeto = json.loads(i)
            print(objeto)

def __generar_indice_usuarios():
    pares = []
    numero_tweet = 0
    indice = OOBTree()

    with open("data.json", "r", encoding = "utf-8") as file:
        for tweet in file:
            try:
                pares.append((json.loads(tweet)["data"]["author_id_hydrate"]["username"], numero_tweet))
            except KeyError:
                print(f"Tweet arrojó un OperationalDisconnect al intentar capturar el tweet número: {numero_tweet} ")
            finally:
                numero_tweet += 1
    for par in pares:
        posting = indice.setdefault(par[0], set())
        posting.add(par[1])
    return indice

def __obtener_tweets_por_fecha(usuario, cantidad_a_imprimir, fecha_desde, fecha_hasta):
        if(usuario):
            if not(indice_usuarios.has_key(usuario)):
                return
            tweets_de_este_usuario = list(indice_usuarios[usuario])
            with open("data.json", "r", encoding="utf-8") as file:
                numero_tweet_actual = 0
                tweet = next(file, None)
                while(tweet and len(tweets_de_este_usuario) > 0 and cantidad_a_imprimir > 0):

                    if numero_tweet_actual in tweets_de_este_usuario:
                        tweet = json.loads(tweet)
                        fecha_del_tweet = datetime.strptime(tweet["data"]["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
                        if(fecha_del_tweet >= fecha_desde and fecha_del_tweet <= fecha_hasta):
                            print("Tweet:")
                            print(tweet["data"]["text"], "\n")
                            cantidad_a_imprimir -= 1
                    numero_tweet_actual += 1
                    tweet = next(file, None)
        else:
            with open("data.json", "r", encoding="utf-8") as file:
                tweet = next(file, None)
                while(tweet and cantidad_a_imprimir > 0):
                    try:
                        tweet = json.loads(tweet)
                        fecha_del_tweet = datetime.strptime(tweet["data"]["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
                        if (fecha_del_tweet >= fecha_desde and fecha_del_tweet <= fecha_hasta):
                            print("Tweet:")
                            print(tweet["data"]["text"],"\n")
                            cantidad_a_imprimir -= 1
                    except KeyError:
                        pass
                    finally:
                        tweet = next(file, None)

indice_usuarios = __generar_indice_usuarios()
#procesar_archivo()
while True:
    search_engine()

