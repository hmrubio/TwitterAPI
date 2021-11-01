from nltk.stem import SnowballStemmer #Stemmer
from nltk.corpus import stopwords #Stopwords
import json
import os
import string
import time

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

        self.__indexar()
    
    
    def __lematizar(self, palabra):
        ''' Usa el stemmer para lematizar o recortar la palabra, previamente elimina todos
        los signos de puntuación que pueden aparecer. El stemmer utilizado también se
        encarga de eliminar acentos y pasar todo a minúscula, sino habría que hacerlo
        a mano'''
        
        #palabra = palabra.decode("utf-8", ignore).encode("utf-8")
        palabra = palabra.strip(string.punctuation + "»" + "\x97" + "¿" + "¡" + "\u201c" +\
                               "\u201d" + "\u2014" + "\u2014l" + "\u00bf")
        # "\x97" representa un guión
        
        palabra_lematizada = self._stemmer.stem(palabra)
        return palabra_lematizada
    
    def __indexar(self):
        n = 0
        lista_bloques = []
        for bloque in self.__parse_next_block():
            bloque_invertido = self.__invertir_bloque(bloque) # ahora cada bloque tine cada palabra con todos los tweets de esa palabra
            lista_bloques.append(self.__guardar_bloque_intermedio(bloque_invertido, n))
            n += 1
        start = time.process_time()
        self.__intercalar_bloques(lista_bloques)
        end = time.process_time()
        print("Intercalar Bloques Elapsed time: ", end-start)
        
        self.__guardar_diccionario_terminos()
   
    def __invertir_bloque(self, bloque):
        bloque_invertido={}
        bloque_ordenado = sorted(bloque,key = lambda tupla: (tupla[0], tupla[1]))
        for par in bloque_ordenado:
            posting = bloque_invertido.setdefault(par[0],set())
            posting.add(par[1]) 
        return bloque_invertido
    
    def __guardar_bloque_intermedio(self, bloque, nro_bloque):
        archivo_salida = "b"+str(nro_bloque)+".json"
        archivo_salida = os.path.join(self._temp, archivo_salida)
        for clave in bloque:
            bloque[clave]=list(bloque[clave])
        with open(archivo_salida, "w+") as contenedor:
            json.dump(bloque, contenedor)
        return archivo_salida
    
    def __intercalar_bloques(self, temp_files):
        
        lista_termID=[str(i) for i in range(len(self._term_to_termID))]
        posting_file = os.path.join(self.salida,"postings.json")
        
        open_files = [open(f, "r") for f in temp_files]

        with open(posting_file,"w+") as salida:
            """for termID in lista_termID:
                posting=set()
                for data in open_files:
                    data.seek(0)
                    bloque = json.load(data)
                    try:
                        posting = posting.union(set(bloque[termID]))
                    except:
                        pass
                json.dump(list(posting), salida, indent=None)
                salida.write("\n")
            """
            # Mal porque por cada término abre y cierra cada uno de los b.json de ./temp

            lista = {}
            for data in open_files:
                bloque = json.load(data)
                for termID in lista_termID:
                    posting = lista.setdefault(termID, set())
                    posting.union(set(bloque[termID]))
            # Mal porque carga todo el índice invertido en memoria.

            print()
    
    def __guardar_diccionario_terminos(self):
        path = os.path.join(self.salida, "diccionario_terminos.json")
        with open(path, "w") as contenedor:
            json.dump(self._term_to_termID, contenedor)
    
    def __parse_next_block(self):
        n = self._blocksize #espacio libre en el bloque actual
        termID = 0 #inicializamos el diccionario de términos
        bloque = [] #lista de pares (termID, tweetID)
        tweetID = 1 # ID de cada tweet, se puede acceder directament desde el json
        with open(self.documento, encoding="utf-8") as file:
            for tweet in file:
                n -= 1
                palabras = json.loads(tweet)['data']['text'].split() # va palabra por palabra del tweet
                for pal in palabras:
                    if pal not in self._stop_words:
                        pal = self.__lematizar(pal)
                        if pal not in self._term_to_termID:
                            self._term_to_termID[pal] = termID
                            termID += 1
                        bloque.append((self._term_to_termID[pal], tweetID))
                tweetID += 1
                if n <=0:
                    yield bloque
                    n = self._blocksize
                    bloque = []
            yield bloque

if ("__main__" == __name__):
    indice = CreacionDeBloques("data.json", "./salida")
