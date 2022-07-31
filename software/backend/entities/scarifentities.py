import dataclasses
import enum
import string
from typing import List
from typing import Optional
from datetime import date
from enum import Enum
from pydantic.dataclasses import dataclass


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

@dataclass
class Institucion ():
    nombre : str
    tipo : str

@dataclass
class Referencia ():
    pass

@dataclass
class Evento ():
    nombre : str
    tipo : TipoEvento
    fecha : date
    pais : str

@dataclass
class Persona ():
    nombre : Optional[str] = None
    def __init__ (self, nombre : str):
        self.nombre = nombre

@dataclass
class Autor ():
    nombre : str
    email : str = None
    oid : str = None
    pais : str = None
    instituciones : List[Institucion] = dataclasses.field(default_factory=list)

    
@dataclass
class Categoria ():
    categoria : str
    codigoScopus : str

@dataclass
class Publicacion ():
    titulo : str
    periodicidad : TipoPeriodicidad = TipoPeriodicidad.NINGUNA
    ISBN : str = None
    fecha : date = None 
    pais : str = None

#
# CLASES PARA GESTION DE EDGES
#
@dataclass
class publicadoEn():
    fecha : date = None
    oid : str = None
    publicacion : Publicacion = None

@dataclass
class ArticuloReferencia():
    titulo : str
    autores : List[Autor] = dataclasses.field(default_factory=list)
    publicacion : Publicacion = None
    pubEn : publicadoEn = None
    oid : str = None
    orcid : str = None

@dataclass
class Articulo ():
    titulo : str
    autores : List[Autor] = dataclasses.field(default_factory=list)
    publicacion : Publicacion = None
    pubEn : publicadoEn = None
    keywords : List[str] = dataclasses.field(default_factory=list)
    text : str = None
    oid : str = None
    orcid : str = None
    referencias : List[ArticuloReferencia] = dataclasses.field(default_factory=list)
