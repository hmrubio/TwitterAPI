
from datetime import *
import json
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
        
    print("\nFechas (dd/mm/aaaa - dd/mm/aaaa):")
    while True:
        try: list_fechas = [datetime.strptime(x.strip(), '%d/%m/%Y') for x in input().split("-")]; break
        except ValueError: print("Una de las dos fechas no es correcta. Pruebe otra vez...")
        
    print("\nHorarios (00:00 - 23:59:")
    while True:
        try: list_horas = [datetime.strptime(x.strip(), '%H:%M') for x in input().split("-")]; break
        except ValueError: print("Una de las dos horas no es correcta. Pruebe otra vez...")
        
    print("\nProcesando...")
    procesar_archivo(nombre_usuario, cantidad_tuits, list_fechas, list_horas)

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

#procesar_archivo()
search_engine()

