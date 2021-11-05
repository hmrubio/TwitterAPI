import datetime
from datetime import *
import json
from BTrees.OOBTree import OOBTree

from _ast import Break

import DiccionarioBloquesInvertido


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

#procesar_archivo()
while True:
    search_engine()

