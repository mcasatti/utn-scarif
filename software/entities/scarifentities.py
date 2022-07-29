import enum
from typing import List
from typing import Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel

#
# CLASES UTILITARIAS
#

class TipoPeriodicidad (Enum):
    NINGUNA = 0
    MENSUAL = 1
    BIMESTRAL = 2
    TRIMESTRAL = 3
    CUATRIMESTRAL = 4
    SEMESTRAL = 5
    ANUAL = 6
    OTRA = 99

class TipoEvento (Enum):
    JORNADA = 'Jornada'
    CONGRESO = 'Congreso'
    WORKSHOP = 'Workshop'

#
# CLASES PARA GESTION DE VERTEX
#

class Institucion (BaseModel):
    nombre : str
    tipo : str

class Articulo (BaseModel):
    titulo : str

class Referencia (BaseModel):
    pass

class Evento (BaseModel):
    nombre : str
    tipo : TipoEvento
    fecha : date
    pais : str

class Persona (BaseModel):
    nombre : str

class Autor (Persona):
    email : str
    oid : str
    pais : str

class Categoria (BaseModel):
    categoria : str
    codigoScopus : str

class Publicacion (BaseModel):
    titulo : str
    periodicidad : TipoPeriodicidad
    ISBN : str
    fecha : date
    pais : str

#
# CLASES PARA GESTION DE EDGES
#
