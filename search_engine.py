import datetime
from datetime import *
import json
import re
import os
import glob
import string
import fileinput
from nltk.stem.snowball import SnowballStemmer
from unidecode import unidecode
import diccionario_bloque_invertido
import buscar_tweets

class BadQueryFormat(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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

        elif (opcion_elegida == 4): agrupar_tweets(); break
            
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
    _obtener_tweets_por_fecha(nombre_usuario, cantidad_tuits, fecha_desde, fecha_hasta)

def consultas_por_palabras():
    print("\nIngrese los siguientes datos por favor...\
    \
    \ni.\tCantidad de tuits (m primeros tuits)\
    \nii.\tConsulta a realizar (por ejemplo: \"Adrián\" and \"Bussiness\")\
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
        if (len(query) == 0):
            print("Debe ingresar una consulta...")
        else:
            try: ejecutar_query(query, cantidad_tuits); break
            except BadQueryFormat:
                print("\nConsulta mal formulada. Vuelva a intentar...")
    

def agrupar_tweets():
    print("\nIngrese los siguientes datos por favor...\
    \
    \ni.\tNombre del primer archivo (con la extension .json)\
    \nii.\tNombre del segundo archivo (con la extension .json)\
    \niii.\tNombre del archivo resultante (con la extension .json)")

    print("\nPrimer archivo: ")
    while True:
        try:
            primer_archivo = input()
            if len(primer_archivo) <= 0 or not primer_archivo.endswith(".json"): raise ValueError
            break
        except ValueError:
            print("El nombre debe contener la extension .json...")

    print("\nSegundo archivo: ")
    while True:
        try:
            segundo_archivo = input()
            if len(segundo_archivo) <= 0 or not segundo_archivo.endswith(".json"): raise ValueError
            break
        except ValueError:
            print("El nombre debe contener la extension .json...")

    print("\nArchivo resultante: ")
    while True:
        try:
            tercer_archivo = input()
            if len(tercer_archivo) <= 0 or not tercer_archivo.endswith(".json"): raise ValueError
            break
        except ValueError:
            print("El nombre debe contener la extension .json...")
    print("\nProcesando...")
    agrupar_tweets_ordenados(primer_archivo,segundo_archivo, tercer_archivo)

def agrupar_tweets_ordenados(file1, file2, salida):

    if not(os.path.exists(file1) and os.path.exists(file2)):
        print("Los archivos no existen")
        return
    with open(file1, "r", encoding="utf-8") as archivo_tweets1, open(file2, "r", encoding="utf-8") as archivo_tweets2, open(salida, "w", encoding="utf-8") as conjunto_tweets:

        tweet_archivo1, fecha_tweet1 = _obtener_tweet_y_fecha(archivo_tweets1)
        tweet_archivo2, fecha_tweet2 = _obtener_tweet_y_fecha(archivo_tweets2)

        while(tweet_archivo1 or tweet_archivo2):
                if(not fecha_tweet1):
                    json.dump(tweet_archivo2, conjunto_tweets,ensure_ascii=False, indent=None)
                    tweet_archivo2, fecha_tweet2 = _obtener_tweet_y_fecha(archivo_tweets2)

                elif(not fecha_tweet2):
                    json.dump(tweet_archivo1, conjunto_tweets,ensure_ascii=False, indent=None)
                    tweet_archivo1, fecha_tweet1 = _obtener_tweet_y_fecha(archivo_tweets1)

                elif(fecha_tweet1 < fecha_tweet2):
                    json.dump(tweet_archivo1, conjunto_tweets,ensure_ascii=False, indent=None)
                    tweet_archivo1, fecha_tweet1 = _obtener_tweet_y_fecha(archivo_tweets1)

                else:
                    json.dump(tweet_archivo2, conjunto_tweets,ensure_ascii=False, indent=None)
                    tweet_archivo2, fecha_tweet2 = _obtener_tweet_y_fecha(archivo_tweets2)
                conjunto_tweets.write("\n")

def _obtener_tweet_y_fecha(archivo_tweet):
    tweet = next(archivo_tweet, None)
    fecha = None
    while(tweet and not fecha):
        try:
            tweet = json.loads(tweet)
            fecha = datetime.strptime(tweet["data"]["created_at"],
                                     '%Y-%m-%dT%H:%M:%S.%fZ')
        except KeyError:
            print("KeyError")
            tweet = next(archivo_tweet, None)
    return(tweet, fecha)

def _obtener_tweets_por_fecha(usuario, cantidad_a_imprimir, fecha_desde, fecha_hasta):
        if(usuario):
            #Busqueda por usuario
            _imprimir_tweets_por_usuario(usuario, cantidad_a_imprimir, fecha_desde, fecha_hasta)
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
                            print("Usuario:")
                            print(tweet["data"]["author_id_hydrate"]["username"])
                            print("Fecha:")
                            print(tweet["data"]["created_at"], "\n")
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

def _imprimir_tweets_por_usuario(usuario, cantidad_restante_a_imprimir, fecha_desde, fecha_hasta):
    tweets_de_este_usuario = [0]
    tweets_de_este_usuario.extend(sorted(_buscar_usuario(usuario)))
    tweet_de_este_usuario_recorridos = 1
    if len(tweets_de_este_usuario) == 1:
        return
    with open("data.json", "r", encoding="utf-8") as file:
        while (tweet_de_este_usuario_recorridos < len(tweets_de_este_usuario) and cantidad_restante_a_imprimir > 0):
            #Avanzar hasta la linea correspondiente
            for x in range(tweets_de_este_usuario[tweet_de_este_usuario_recorridos-1]+1, tweets_de_este_usuario[tweet_de_este_usuario_recorridos]):
                next(file, None)

            # Compruebo que el tweet esté entre el rango de fechas
            tweet = json.loads(next(file, None))
            fecha_del_tweet = datetime.strptime(tweet["data"]["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
            if (fecha_del_tweet >= fecha_desde and fecha_del_tweet <= fecha_hasta):
                print("Tweet:")
                print(tweet["data"]["text"])
                print("Usuario:")
                print(tweet["data"]["author_id_hydrate"]["username"])
                print("Fecha:")
                print(tweet["data"]["created_at"],"\n")
                cantidad_restante_a_imprimir -= 1
            tweet_de_este_usuario_recorridos += 1

def _reducir(palabra):
    # palabra = palabra.strip(string.punctuation + "»" + "\x97" + "¿" + "¡" + "\u201c" + \
    #                             "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
    # palabra_lematizada = SnowballStemmer("spanish", ignore_stopwords=False).stem(palabra)

    palabra = unidecode(palabra).lower()
    condition = re.compile(r'[a-z0-9]+')
    palabra_a_armar = condition.findall(palabra)
    palabra_out = ""
    for word in palabra_a_armar:
        palabra_out = palabra_out + word

    return palabra_out

def _buscar_palabra(palabra):
    if (palabra != "*"):
        palabra = _reducir(palabra.strip('"'))
        with open("./output/diccionario_terminos.json", "r") as contenedor:
            # linea = next(contenedor, False)
            # while (linea):
            #     linea = json.loads(linea)
            #     if (palabra in linea[0]):
            #         break
            #     else:
            #         linea = next(contenedor, False)
            linea = list()
            for i in contenedor:
                aux = json.loads(i)
                if palabra in aux[0]:
                    linea.append(aux)

            if len(linea) == 0: linea = False

    else: linea = "Comodin"

    conjunto = set()
    if (linea == "Comodin"): # Devuelve todos los docIDs.
        with open("./output/postings.json", "r") as contenedor:
            while(contenedor):
                try: conjunto.update(json.loads(next(contenedor)))
                except StopIteration: break
    elif (linea): # Encontró el término buscado.
        with open("./output/postings.json", "r") as contenedor:
            # for i in range(1, linea[1]):
            #     valor = next(contenedor)
            # conjunto.update(json.loads(next(contenedor)))
            lines_swifted = 1
            for i in contenedor:
                if (len(linea) > 0 and linea[0][1] == lines_swifted):
                    conjunto.update(json.loads(i))
                    linea.pop(0)
                lines_swifted += 1

    return conjunto

def _buscar_palabras(query):
    query = query.lower()
    matches = re.findall(r'\([^()]+\)|\"(?:[^\"]+)\"|and not|and|not|or', query)
    #print(matches)

    if (len(matches) % 2 == 0): 
        if (matches[0] == "not"):
            matches[0] = "and not"
            matches.insert(0, "*")
        else: 
            raise BadQueryFormat("Falta un operador que vincule dos términos: " + query)

    out = set()
    for i in range(0, len(matches), 2):
        if matches[i][0] == "(":
            conjunto = _buscar_palabras(matches[i].strip("()"))
            
        elif (type(matches[i]) != type(set)):
            texto = re.findall(r'\S+', matches[i])
            conjunto = set()
            if (len(texto) > 1):
                for palabra in texto:
                    conjunto.update(_buscar_palabra(palabra))
            else:
                conjunto = _buscar_palabra(matches[i])

        operador = ""
        if ((i - 1) > 0):
            operador = matches[i - 1]
        elif (i == 0):
            out.update(conjunto)

        if (operador == "and"):
            out.intersection_update(conjunto)
        elif (operador == "or"):
            out.update(conjunto)
        elif (operador == "and not" or operador == "not"):
            out.difference_update(conjunto)

    return out

def ejecutar_query(query, cantidad_tweets):
    lista = list(_buscar_palabras(query))
    lista.sort()
    
    print("\n------------------------------------------------------------------------")
    tamanio_lista = len(lista)
    with open("data.json", encoding="utf-8") as file:
        lines_swifted = 0
        while (cantidad_tweets > 0
            and len(lista) > 0):
            posicion = lista.pop(0)
            while (lines_swifted < posicion): # Tweet encontrado
                line = next(file)
                lines_swifted += 1

            cantidad_tweets -= 1
            text = json.loads(line)['data']['text']
            print()
            print(text, '\n')
            print("Numero de tweet: ", lines_swifted, "\n")
            print("------------------------------------------------------------------------")
    print("\nCantidad de Tweets encontrados: ", tamanio_lista)

if (__name__ == "__main__"):
    while True:
        search_engine()