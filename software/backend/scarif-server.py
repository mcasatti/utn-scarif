'''
Server Web que implementará la API de Sibila.
Por el momento es simplemente un sandbox para hacer algunas
pruebas de las librerías de Python y otros conceptos.
'''

from starlette.responses import Response
from typing import Dict, List,Tuple
from entities.scarifentities import Articulo
import logging
from rich.logging import RichHandler
from managers.cienciomanager import CiencioManager
from fastapi import FastAPI, Request, Body
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

cm = CiencioManager(
    host=os.getenv('PB_DB_HOST','http://localhost'),       # HOST
    port=os.getenv('PB_DB_PORT', 2480),              # PORT
    user=os.getenv('PB_DB_USER','root'),           # USER
    password=os.getenv('PB_DB_PASS', 'kymosadmin117') # PASSWORD
)

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
    return {"Scariff Server": "Servidor Web Scariff (FastAPI/Python)"}


@app.get("/articulos/")
async def getArticulos(request: Request):
    params = dict(request.query_params)
    filter_str = params.get('filter', "")
    filter = " and ".join(filter_str.split(","))
    return cm.getArticulos(
        filter=filter,
        limit=params.get('limit', 5)
    )

def run(): 
    """
    This function to run configured uvicorn server.
    """
    uvicorn.run("scariff-server:app", 
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
