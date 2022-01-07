'''
Server Web que implementará la API de Sibila.
Por el momento es simplemente un sandbox para hacer algunas
pruebas de las librerías de Python y otros conceptos.
'''

from starlette.responses import JSONResponse, Response
from typing import Dict, List,Tuple
from entities.graphclasses import Concepto,Relacion,Equivalencia
import logging
from rich import print,inspect
from rich.logging import RichHandler
from managers.knowledgemanager import KnowledgeManager
from managers.textmanager import TextManager
from fastapi import FastAPI, Request, Body
from fastapi.encoders import jsonable_encoder
from http import HTTPStatus
from json.decoder import JSONDecodeError
from managers.dbmanager import DBException
from multiprocessing import Process
import os
import asyncio
import signal
import uvicorn
import random

FORMAT = "%(message)s"
#logging.basicConfig(level=logging.INFO,handlers=[RichHandler()])
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

km = KnowledgeManager(
    host=os.getenv('PB_DB_HOST','http://localhost'),       # HOST
    port=os.getenv('PB_DB_PORT',2480),              # PORT
    user=os.getenv('PB_DB_USER','admin'),           # USER
    password=os.getenv('PB_DB_PASS','admin')        # PASSWORD
)

gm = GraphicManager()

tm = TextManager()

app = FastAPI()

'''
Los VERBOS (prefijos de los métodos) van a ser:
INS: Insertar un nuevo registro
DEL: Eliminar un registro existente
UPD: Modificar un registro existente
GET: Obtener información
'''

@app.get("/")
async def read_root():
    return {"Sibila Server": "Servidor Web Sibila (FastAPI/Python)"}


'''
METODOS para gestionar CONCEPTOS
'''
@app.get("/conceptos/")
async def getConceptos(request : Request):
    try:
        body = await request.json();
        return km.getConceptos(
            keys=body.get('filter',None),
            limit=body.get('limit',None)
        )
    except JSONDecodeError as e:
        return Response(content=e.msg,status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/conceptos/complejos")
async def getConceptosComplejos(request : Request):
    return km.getConceptosComplejos()

@app.post("/concepto/")
async def insConcepto(concepto : Concepto):
    try:
        result,id = km.insConcepto(concepto)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.put("/concepto/")
async def updConcepto(oldConcepto : Concepto, newConcepto : Concepto):
    try:
        result = km.updConcepto(oldConcepto,newConcepto)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.delete("/concepto/")
async def delConcepto(concepto : Concepto):
    try:
        result = km.delConcepto(concepto)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/concepto/refs")
async def getRefsConcepto (concepto : Concepto):
    refs = km.getRefsConcepto(concepto)
    return {"references":refs}

@app.get("/concepto/equivalencias")
async def getEquivalencias (concepto : Concepto):
    equivalencias = km.getEquivalencias(concepto = concepto)
    return {"equivalencias":equivalencias}

@app.post("/concepto/equivalencias")
async def insEquivalencia (concepto : Concepto, equivalencia : Equivalencia):
    return km.insEquivalencia(
        concepto = concepto,
        equivalencia=equivalencia.Nombre,
        peso=equivalencia.Peso
        )

@app.delete("/concepto/equivalencias")
async def insEquivalencia (concepto : Concepto, equivalencia : Equivalencia):
    return km.delEquivalencia(
        concepto = concepto,equivalencia=equivalencia.Nombre
        )


'''
METODOS para gestionar RELACIONES
'''
@app.get("/relaciones")
async def getRelaciones(request : Request):
    try:
        body = await request.json();
        return km.getRelaciones(
            keys=body.get('filter',None),
            limit=body.get('limit',None)
        )
    except JSONDecodeError as e:
        return Response(content=e.msg,status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    
@app.get("/relaciones/complejas")
async def getRelacionesComplejas():
    return km.getRelacionesComplejas()

@app.post("/relacion")
async def insRelacion(origen: Concepto, relacion: Relacion, destino: Concepto):
    try:
        result = km.insRelacion(conceptoOrigen=origen, relacion=relacion, conceptoDestino=destino)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.post("/tiporelacion")
async def insRelacion(tiporelacion : str = Body(..., embed=True)):
    # Body(...,embed=True) sirve para aceptar un tipo de datos básico como json en lugar de un objeto
    try:
        result = km.addTipoRelacion(nombreTipo=tiporelacion)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

'''
METODOS para gestionar ESTRUCTURAS
'''
@app.post("/estructura")
async def insEstructura (origen : Concepto, relacion : Relacion, destino : Concepto):
    try:
        result = km.insStruct(conceptoOrigen=origen, relacion=relacion, conceptoDestino=destino)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

'''
METODOS para gestionar RUTAS
'''
@app.get("/path")
async def getPath (conceptoInicial : Concepto, conceptosIncluidos : List[str]):
    try:
        result = km.getPath(
            conceptoInicial=conceptoInicial,
            conceptosIncluidos=conceptosIncluidos
        )
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/path/depth")
async def getPathDepth (conceptoInicial : Concepto, depth : int = Body(..., embed=True)):
    try:
        result = km.getPathsFrom(
            conceptoInicial=conceptoInicial,
            profundidad=depth
        )
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/path/type")
async def getPathByType (relacion : Relacion):
    try:
        result = km.getPathsByType(relacion=relacion)
        return result
    except DBException as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


'''
METODOS para gestionar la ortografía y procesamiento de texto
'''
@app.get("/text/check")
async def getTextCheck (texto : str = Body(...,embed=True), full : bool = Body(default=False,embed=True)):
    try:
        result = tm.check(texto=texto,full=full)
        return result
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/text/tokenize")
async def getTextTokens (texto : str = Body(...,embed=True)):
    try:
        correcciones,tokens = tm.tokenize(texto=texto)
        res = {
            "correcciones" : correcciones,
            "terminos" : tokens
        }
        return res
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.post("/text/dictionary/word")
async def insDictionaryWord (word : str = Body(...,embed=True)):
    try:
        result = tm.addWordToDict(word=word)
        return result
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.post("/text/dictionary/words")
async def insDictionaryWords (words : List[str] = Body(...,embed=True)):
    try:
        result = tm.addWordsToDict(words=words)
        return result
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/text/dictionary")
async def getDictionary ():
    try:
        result = {"dictionary" : tm.getDictionary()}
        return result
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.delete("/text/dictionary/word")
async def delFromDictionary (word : str):
    try:
        result = tm.delWordFromDict(word=word)
        return result
    except Exception as e:
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

'''
METODOS para gestionar las respuestas y la evaluación
'''
@app.post("/respuesta/evaluar")
async def corregirRespuesta (respuestaBase : str= Body(...,embed=True), respuestaAlumno : str= Body(...,embed=True)):
    try:
        result = {"puntaje":round(random.uniform(0,1),2)}
        return result
    except Exception as e:
        return Response(content=str(e), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.post("/respuesta/tokenize")
async def tokenizeRespuesta (respuesta : str= Body(...,embed=True), includeStopWords : bool = Body(...,embed=True)):
    try:
        correcciones,tokens = km.tokenizeRespuesta(texto=respuesta,textManager=tm,includeStopWords=includeStopWords)
        res = {
            "correcciones" : correcciones,
            "terminos" : tokens
        }
        return res
    except Exception as e:
        inspect(e)
        return Response(content=e.message, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)



















def run(): 
    """
    This function to run configured uvicorn server.
    """
    uvicorn.run("sibila-server:app", 
        host=os.getenv('PB_LISTENING_IP',"0.0.0.0"), 
        port=int(os.getenv('PB_LISTENING_PORT',8000)), 
        #reload=True,
        log_config = None
        )

def start():
    """
    This function to start a new process (start the server).
    """
    global proc
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    proc = Process(target=run, args=(), daemon=True)
    proc.start()


def stop(): 
    """
    This function to join (stop) the process (stop the server).
    """
    global proc
    # check if the process is not None
    if proc: 
        # join (stop) the process with a timeout setten to 0.25 seconds.
        # using timeout (the optional arg) is too important in order to
        # enforce the server to stop.
        proc.join(0.25)

if __name__ == "__main__":
    # La siguiente linea la sugieren para poder depurar interactivamente desde vscode
    # multiprocessing.set_start_method('spawn', True)
    
    # to start the server call start function.
    start()
    
    # to stop the server call stop function.
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(stop())
        )

'''
METODOS PARA graficar los grafos.

'''
@app.get("/grafico/one")
async def showOneResponse (conceptosRelaciones : List[str], relacionesSolo : List[str] = []):
    try:
        result = gm.showOneResponse(
            conceptosRelaciones,
            relacionesSolo
        )
        return result
    except:
        return Response(content='Error Graficando', status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/grafico/plenty")
async def showMultipleResponse (conceptosRelaciones : List[str], relacionesSolo : List[str] = []):
    try:
        result = gm.showMultipleResponse(
            conceptosRelaciones,
            relacionesSolo
        )
        return result
    except:
        return Response(content='Error Graficando', status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


