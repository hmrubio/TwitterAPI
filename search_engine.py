import datetime
from datetime import *
import json
from queue import PriorityQueue
import re
import os
import glob
import string
import fileinput
from nltk.stem.snowball import SnowballStemmer
import diccionario_bloque_invertido
import buscar_tweets

def search_engine():
    print("\nBuscador de información recopilada...\
    \nIngrese la opción que desea utilizar.\
    \
    \n1.\tConsultas por fecha y hora.\
    \n2.\tConsultas de palabras o frases.\
    \n3.\tBuscar más tweets.\
    \n4.\tOrdenar tweets.\
    \n5.\tFinalizar.\
    \
    \n\nOpción número: ")
    
    while True:
        try: opcion_elegida = int(input())
        except ValueError: opcion_elegida = 0
        
        if (opcion_elegida == 1): consultas_por_fechahora(); break
        
        elif (opcion_elegida == 2): consultas_por_palabras(); break

        elif (opcion_elegida == 3): buscar_tweets.BuscarTweets(); break

        elif (opcion_elegida == 4): ordenar_tweets(); break
            
        elif (opcion_elegida == 5): break
            
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
        query = input()
        if (len(query) != 0): break
        print("Debe ingresar una consulta...")
    
    print("\n------------------------------------------------------------------------")
    ejecutar_query(query, cantidad_tuits)

def ordenar_tweets():
    files = glob.glob("./ordenar/*")

    queue = PriorityQueue()

    with open("data.json.bak", "w+") as new_file:
        try:
            for line in fileinput.input(files[1]):
                line = json.loads(line)
                fecha_creacion = datetime.strptime(line["data"]["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
                queue.put(line, fecha_creacion)
        except UnicodeDecodeError:
            pass
        
        while (queue.not_empty):
            json.dump(queue.get(), new_file)
            

def __obtener_tweets_por_fecha(usuario, cantidad_a_imprimir, fecha_desde, fecha_hasta):
        if(usuario):
            #Busqueda por usuario
            imprimir_tweets_por_usuario(usuario, cantidad_a_imprimir, fecha_desde, fecha_hasta)
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
                        
def _buscar_usuario(palabra):
    palabra = palabra.strip("")
    with open("output/diccionario_usuarios.json", "r") as contenedor:
        linea = next(contenedor, False)
        while (linea):
            linea = json.loads(linea)
            if (linea[0] == palabra):
                break
            else:
                linea = next(contenedor, False)

    conjunto = set()
    if (linea):
        with open("output/user_postings.json", "r") as contenedor:
            for i in range(1, linea[1]):
                next(contenedor)
            conjunto.update(json.loads(next(contenedor)))
    return conjunto

def imprimir_tweets_por_usuario(usuario, cantidad_restante_a_imprimir, fecha_desde, fecha_hasta):
    tweets_de_este_usuario = [1]
    tweets_de_este_usuario.extend(sorted(_buscar_usuario(usuario)))
    tweet_de_este_usuario_recorridos = 1
    if len(tweets_de_este_usuario) == 1:
        return
    with open("data.json", "r", encoding="utf-8") as file:
        while (tweet_de_este_usuario_recorridos < len(tweets_de_este_usuario) and cantidad_restante_a_imprimir > 0):
            #Avanzar hasta la linea correspondiente
            for x in range(tweets_de_este_usuario[tweet_de_este_usuario_recorridos-1], tweets_de_este_usuario[tweet_de_este_usuario_recorridos]):
                next(file, None)

            # Compruebo que el tweet esté entre el rango de fechas
            tweet = json.loads(next(file, None))
            fecha_del_tweet = datetime.strptime(tweet["data"]["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (fecha_del_tweet >= fecha_desde and fecha_del_tweet <= fecha_hasta):
                print("Tweet:")
                print(tweet["data"]["text"], "\n")
                cantidad_restante_a_imprimir -= 1
            tweet_de_este_usuario_recorridos += 1

def _lematizar(palabra):
    palabra = palabra.strip(string.punctuation + "»" + "\x97" + "¿" + "¡" + "\u201c" + \
                                "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
    palabra_lematizada = SnowballStemmer("spanish", ignore_stopwords=False).stem(palabra)
    return palabra_lematizada

def _buscar_palabra(palabra):
    palabra = _lematizar(palabra.strip('"'))
    with open("./salida/diccionario_terminos.json", "r") as contenedor:
        linea = next(contenedor, False)
        while (linea):
            linea = json.loads(linea)
            if (linea[0] == palabra):
                break
            else:
                linea = next(contenedor, False)

    conjunto = set()
    if (linea):
        with open("./salida/postings.json", "r") as contenedor:
            for i in range(1, linea[1]):
                valor = next(contenedor)
            conjunto.update(json.loads(next(contenedor)))

    return conjunto

def _buscar_palabras(query):
    matches = re.findall(r'\([^()]+\)|\"(?:[^\"]+)\"|and not|and|not|or', query)
    #print(matches)

    out = set()
    for i in range(0, len(matches), 2):
        if matches[i][0] == "(":
            conjunto = _buscar_palabras(matches[i].strip("()"))
        elif (type(matches[i]) != type(set)):
            conjunto = _buscar_palabra(matches[i])

        if ((i - 1) > 0):
            operador = matches[i - 1]
        elif (i == 0):
            out.update(conjunto)
            operador = ""
        else:
            operador = ""

        if (operador == "and"):
            out.intersection_update(conjunto)
        elif (operador == "or"):
            out.update(conjunto)
        elif (operador == "and not"):
            out.difference_update(conjunto)

    return out

def ejecutar_query(query, cantidad_tweets):
    lista = list(_buscar_palabras(query))
    lista.sort()
    
    with open("data.json", encoding="utf-8") as file:
        # i = 0

        # for tweet_number in conjunto:
        #     tweet = file.readlines()[tweet_number]
        #     file.seek(0)
        #     text = json.loads(tweet)['data']['text']
        #     print(text, '\n')

        #     if i >= 15:
        #         break
        #     i += 1

        lines_swifted = 0
        while (cantidad_tweets > 0
            and len(lista) > 0):
            posicion = lista.pop(0) + 1
            while (lines_swifted < posicion): # Tweet encontrado
                line = next(file)
                lines_swifted += 1

            cantidad_tweets -= 1
            text = json.loads(line)['data']['text']
            print()
            print(text, '\n')
            print("------------------------------------------------------------------------")

if (__name__ == "__main__"):
    while True:
        search_engine()

