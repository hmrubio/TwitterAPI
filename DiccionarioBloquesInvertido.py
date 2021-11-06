import datetime

from nltk.stem import SnowballStemmer  # Stemmer
from nltk.corpus import stopwords  # Stopwords
import json
import os
import string
import time
import re

"""Anotaciones:
_Hay que cambiar el sistema de intercalado de bloques invertidos.
"""


class CreacionDeBloques:
    def __init__(self, documento, salida, temp="./temp", language='spanish'):
        ''' documentos: carpeta con archivos a indexar
            salida: carpeta donde se guardará el índice invertido'''
        self.documento = documento
        self.salida = salida
        self._blocksize = 5000
        self._temp = temp
        self._stop_words = frozenset(stopwords.words(language))  # lista de stop words
        self._stemmer = SnowballStemmer(language, ignore_stopwords=False)
        self._term_to_termID = {}
        self._user_to_userID = {}

        self.__indexar()

    def __lematizar(self, palabra):
        ''' Usa el stemmer para lematizar o recortar la palabra, previamente elimina todos
        los signos de puntuación que pueden aparecer. El stemmer utilizado también se
        encarga de eliminar acentos y pasar todo a minúscula, sino habría que hacerlo
        a mano'''

        # palabra = palabra.decode("utf-8", ignore).encode("utf-8")
        palabra = palabra.strip(string.punctuation + "»" + "\x97" + "¿" + "¡" + "\u201c" + \
                                "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
        # "\x97" representa un guión

        palabra_lematizada = self._stemmer.stem(palabra)
        return palabra_lematizada

    def __indexar(self):
        n = 0
        lista_bloques_palabras = []
        lista_bloques_usuarios= []
        for bloque_palabras,bloque_usuarios in self.__parse_next_block():
            bloque_invertido_palabras = self.__invertir_bloque(
                bloque_palabras)            # ahora cada bloque tine cada palabra con todos los tweets de esa palabra

            bloque_invertido_usuarios = self.__invertir_bloque(
                bloque_usuarios)            # ahora cada bloque tine cada usuario con todos los tweets de esa usuario

            lista_bloques_palabras.append(self.__guardar_bloque_intermedio(bloque_invertido_palabras, n))
            lista_bloques_usuarios.append(self.__guardar_bloque_intermedio(bloque_invertido_usuarios, f"u{n}"))
            n += 1
        start = time.process_time()
        self.__intercalar_bloques(lista_bloques_palabras, self._term_to_termID, "postings")
        self.__intercalar_bloques(lista_bloques_usuarios,self._user_to_userID,"user_postings")
        end = time.process_time()
        print("Intercalar Bloques Elapsed time: ", end - start)

        self.__guardar_diccionario_terminos(self._term_to_termID, "terminos")
        self.__guardar_diccionario_terminos(self._user_to_userID, "usuarios")

    def __invertir_bloque(self, bloque):
        bloque_invertido = {}
        bloque_ordenado = sorted(bloque, key=lambda tupla: (tupla[0], tupla[1]))
        for par in bloque_ordenado:
            posting = bloque_invertido.setdefault(par[0], set())
            posting.add(par[1])
        return bloque_invertido

    def __guardar_bloque_intermedio(self, bloque, nro_bloque):
        archivo_salida = "b" + str(nro_bloque) + ".json"
        archivo_salida = os.path.join(self._temp, archivo_salida)
        for clave in bloque:
            bloque[clave] = list(bloque[clave])
        with open(archivo_salida, "w+") as contenedor:
            json.dump(bloque, contenedor)
        return archivo_salida

    def __intercalar_bloques(self, temp_files, term_to_termID, nombre_archivo_salida):

        lista_termID = [str(value) for value in term_to_termID.values()]
        iter_lista = iter(lista_termID)
        cantidad_term_group = len(lista_termID) // 1000 + 1

        posting_file = os.path.join(self.salida, f"{nombre_archivo_salida}.json")
        open_files = [open(f, "r") for f in temp_files]

        with open(posting_file, "w+") as salida:

            for x in range(cantidad_term_group):
                postings = {}
                lista_parte_term_ID = [next(iter_lista, None) for i in range(1000)]

                for data in open_files:
                    data.seek(0)
                    bloque = json.load(data)

                    i = 0
                    while i < 1000 and lista_parte_term_ID[i]:
                        try:
                            postings[i] = postings.setdefault(i,set()).union(set(bloque[lista_parte_term_ID[i]]))
                        except:
                            pass
                        i += 1
                for posting in postings.values():
                    json.dump(list(posting), salida, indent=None)
                    salida.write('\n')

    def __guardar_diccionario_terminos(self, term_to_termID, nombre_archivo_diccionario):
        path = os.path.join(self.salida, f"diccionario_{nombre_archivo_diccionario}.json")
        with open(path, "w") as contenedor:
            for term, termID in term_to_termID.items():
                json.dump((term, termID), contenedor)
                contenedor.write("\n")

    def __parse_next_block(self):
        n = self._blocksize  # espacio libre en el bloque actual
        termID = 1  # inicializamos el diccionario de términos
        userID = 1  # inicializamos el diccionario de términos
        bloque_palabras = []  # lista de pares (termID, tweetID)
        bloque_usuarios = []

        tweetID = 0  # ID de cada tweet, se puede acceder directament desde el json
        with open(self.documento, encoding="utf-8") as file:
            for tweet in file:
                n -= 1
                #Recorro las palabras
                palabras = json.loads(tweet)['data']['text'].split()  # va palabra por palabra del tweet
                for pal in palabras:
                    if pal not in self._stop_words:
                        #pal = self.__lematizar(pal)
                        if pal not in self._term_to_termID:
                            self._term_to_termID[pal] = termID
                            termID += 1
                        bloque_palabras.append((self._term_to_termID[pal], tweetID))

                #Recorro los usuarios
                usuario = json.loads(tweet)["data"]["author_id_hydrate"]["username"]
                if usuario not in self._user_to_userID:
                    self._user_to_userID[usuario] = userID
                    userID += 1
                bloque_usuarios.append((self._user_to_userID[usuario], tweetID))


                tweetID += 1
                if n <= 0:
                    yield(bloque_palabras,bloque_usuarios)
                    n = self._blocksize
                    bloque_palabras = []
                    bloque_usuarios = []
            yield(bloque_palabras,bloque_usuarios)

    @staticmethod
    def _buscar_palabra(palabra):
        palabra = palabra.strip('"')
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

    @staticmethod
    def buscar_palabras(query, cantidad_tweets):

        matches = re.findall(r'\([^()]+\)|\"(?:[^\"]+)\"|and not|and|not|or', query)

        print(matches)

        out = set()
        for i in range(0, len(matches), 2):
            if matches[i][0] == "(":
                conjunto = CreacionDeBloques.buscar_palabras(matches[i].strip("()"), cantidad_tweets)
            elif (type(matches[i]) != type(set)):
                conjunto = CreacionDeBloques._buscar_palabra(matches[i])

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


if ("__main__" == __name__):
    algo = CreacionDeBloques._buscar_palabra("cambio")
    conjunto = CreacionDeBloques.buscar_palabras('"cambio" and ("presidente" or "Google")', 10)
    #conjunto = CreacionDeBloques.buscar_palabras('" Potro" or ("Murray" and not "Copa Davis") or "Persona"', 10)
    print(conjunto)

    with open("data.json", encoding="utf-8") as file:
        i = 0

        for tweet_number in conjunto:
            tweet = file.readlines()[tweet_number]
            file.seek(0)
            text = json.loads(tweet)['data']['text']
            print(text, '\n')
            if i >= 15:
                break
            i += 1