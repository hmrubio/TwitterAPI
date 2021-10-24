
from datetime import *

def search_engine():
    print("\nBuscador de información recopilada...\
    \nIngrese la opción que desea utilizar.\
    \
    \n1.\tConsultas por fecha y hora.\
    \n2.\tConsultas de palabras o frases.\
    \
    \n\nOpción número: ")
    
    opcion_elegida = input()
    
    switcher = {
        1: consultas_por_fechahora()
        }
    
    switcher.get(opcion_elegida)

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
        except ValueError: print("Ingrese cantidad de tuits vàlido...")
        
    print("\nFechas (dd/mm/aaaa - dd/mm/aaaa):")
    while True:
        try: fechas = [datetime.strptime(x.strip(), '%d/%m/%Y') for x in input().split("-")]; break
        except ValueError: print("Una de las dos fechas no es correcta. Pruebe otra vez...")
        
    print("\nHorarios (00:00 - 23:59:")
    while True:
        try: fechas = [datetime.strptime(x.strip(), '%H:%M') for x in input().split("-")]; break
        except ValueError: print("Una de las dos horas no es correcta. Pruebe otra vez...")
        
    print("\nProcesando...")

search_engine()

