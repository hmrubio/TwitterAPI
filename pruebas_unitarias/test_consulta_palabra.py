import search_engine
from datetime import *

def test_google_not_google_aparece_0_veces():
    conjunto = search_engine._buscar_palabras('"Google" not "Google"')

    assert len(conjunto) == 0

def test_google_aparece_898_veces():
    conjunto = search_engine._buscar_palabras('"Google"')

    assert len(conjunto) == 898

def test_26_tweets_no_son_utiles():
    conjunto = search_engine._buscar_palabras('NOT "cambio climático" NOT "sequía" NOT "calentamiento global" NOT "economía circular" NOT "espacio verde" NOT "protección ambiental"')

    assert len(conjunto) == 26