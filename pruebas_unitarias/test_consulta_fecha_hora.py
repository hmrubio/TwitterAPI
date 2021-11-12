import search_engine
from datetime import *

def test_consulta_por_fecha_trae_10_tweets():
    fecha_desde = datetime.strptime("10/11/2021 00:01", '%d/%m/%Y %H:%M')
    fecha_hasta = datetime.strptime("12/11/2021 18:00", '%d/%m/%Y %H:%M')
    lista = search_engine._obtener_tweets_por_fecha(None, 10, fecha_desde, fecha_hasta)

    assert len(lista) == 10

def test_consulta_por_fecha_trae_11_tweets_para_ElUniversalMx_usuario():
    fecha_desde = datetime.min
    fecha_hasta = datetime.max
    lista = search_engine._imprimir_tweets_por_usuario("El_Universal_Mx", 100, fecha_desde, fecha_hasta)

    assert len(lista) == 11