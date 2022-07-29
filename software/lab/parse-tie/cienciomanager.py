
from typing import Dict, List,Tuple
from dbmanager import DBManager
import re
import json
import logging
from rich.logging import RichHandler
from rich import print,inspect
from scarifentities import Articulo, ArticuloReferencia,Autor, Institucion

class CiencioException (Exception):
    message : str = None
    def __init__(self,message : str):
        self.message = message
        super().__init__(self.message)

class CiencioManager:
    db : DBManager = None  
    
    """
    Concept Manager:
    Clase que engloba todas las operaciones de gestión de entidades cienciométricas y relaciones en OrientDB
    """
    def __init__ (self, host='http://localhost', port=2480, database='utn-scarif', user='admin', password='admin'):        
        self.db = DBManager(host=host,port=port,database=database,user=user,password=password)   
    
    '''
    Los VERBOS de la gestión de la base de conocimiento van a ser:
    INS: Insertar un nuevo registro
    DEL: Eliminar un registro existente
    UPD: Modificar un registro existente
    GET: Obtener información
    '''

    '''
    -----------------------------------------------------------------------------------------
    TODO: TODOS LOS METODOS QUE INSERTEN O ACTUALICEN INFORMACION DE ENTIDADES DEBEN DEVOLVER
    EN EL RETORNO, UN OBJETO CON LOS DATOS ACTUALIZADOS
    ''' 

    #--------------------------------------------------------------------------------------------
    # GESTION DE Autores
    # --------------------------------------------------------------------------------------------
    '''
    Grabar un autor en la base de datos.
    Si tiene instituciones las graba y asocia
    '''
    def insAutor (self, aut : Autor) -> Tuple[str,int]:
        # Ignorar si viene un autor llamado , (que quiere decir que no se detectó el nombre)
        if aut.nombre.strip() == ',' or aut.nombre.strip() == '' or aut.nombre == None:
            return None,0

        if not self.db.existVertex(classname="Autor",keys={"nombre":aut.nombre}):
            result,id = self.db.insVertex(
                classname="Autor",
                fields={
                    "nombre" : aut.nombre,
                    "email" : aut.email,
                    "oid" : aut.oid,
                    "pais" : aut.pais,
                    #instituciones : List[Institucion] = dataclasses.field(default_factory=list)
                    }
                )
        else:
            
            result = self.db.getVertex(classname="Autor",keys={"nombre":aut.nombre})
            id = self.db.extractId(result)

        logging.info ("Result insAutor: {} - ID: {}".format(result,id))
        # Si el autor tiene instituciones asociadas grabarlas y relacionarlas
        for inst in aut.instituciones:
            result_inst, id_inst = self.insInstitucion(inst=inst)
            # Despues de grabar la institucion grabar la relacion
            if id_inst:
                self.insFiliacionA (autor=aut,institucion=inst)

        return result,id    
    '''
    Graba la relacion entre un autor y un articulo
    '''
    def insAutorDe (self, autor : Autor, articulo : Articulo):
        result = self.db.insEdge(
            sourceClass='Autor',
            sourceCondition={'nombre':autor.nombre},
            destClass='Articulo',
            destCondition={'titulo':articulo.titulo},
            edgeClass='autorDe',
            unique=True
            )
        logging.info ("Result insAutorDe: {}->{} - ID: {}".format(autor.nombre,articulo.titulo,result))
        return result

    #--------------------------------------------------------------------------------------------
    # GESTION DE Instituciones
    # --------------------------------------------------------------------------------------------
    '''
    Graba una institucion en la base de datos
    '''
    def insInstitucion (self, inst : Institucion) -> Tuple[str,int]:
        # Ver si la institucion no existe
        if not self.db.existVertex(classname="Institucion",keys={"nombre" : inst.nombre}):
            logging.info ("La institucion no existe, darla de alta")
            result,id = self.db.insVertex(
                classname="Institucion",
                fields={
                    "nombre" : inst.nombre,
                    "tipo" : inst.tipo
                    }
                )
            logging.info ("Result insInstitucion: {} - ID: {}".format(result,id))
            return result,id
        else:
            res_qry = self.db.getVertex(classname="Institucion",keys={"nombre" : inst.nombre})
            rid = self.db.extractId(result=res_qry)
            # Si se encontró volver con el result y el id encontrados
            logging.info ("La institucion ya existe: {} - RID: {}".format(res_qry,rid))
            return res_qry,rid

    '''
    Graba la relacion entre un autor y una institucion (filiacion)
    '''
    def insFiliacionA (self, autor : Autor, institucion : Institucion):
        result = self.db.insEdge(
            sourceClass='Autor',
            sourceCondition={'nombre':autor.nombre},
            destClass='Institucion',
            destCondition={'nombre':institucion.nombre},
            edgeClass='filiacionA',
            unique=True
            )
        logging.info ("Result insFiliacionA: {}->{} - ID: {}".format(autor.nombre,institucion.nombre,result))
        return result

    '''
    Graba la relacion entre un articulo y otro articulo (referenciado)
    '''
    def insReferenciaA (self, art : Articulo, artref : ArticuloReferencia):
        result = self.db.insEdge(
            sourceClass='Articulo',
            sourceCondition={'titulo':art.titulo},
            destClass='Articulo',
            destCondition={'titulo':artref.titulo},
            edgeClass='referenciaA',
            unique=True
            )
        logging.info ("Result insReferenciaA: {}->{} - ID: {}".format(art.titulo,artref.titulo,result))
        return result

    #--------------------------------------------------------------------------------------------
    # GESTION DE Articulos
    # --------------------------------------------------------------------------------------------
    '''
    Graba un articulo en la base de datos.
    Graba y asocia todas las entidades relacionadas, como ser autores,
    instituciones, keywords, referencias, etc.
    '''
    def insArticulo (self,art : Articulo) -> Tuple[str,int]:
        if not self.db.existVertex (classname="Articulo",keys={"titulo":art.titulo}):
            result,id = self.db.insVertex(
                classname="Articulo",
                fields={
                    "titulo" : art.titulo,
                    #autores : List[Autor] = dataclasses.field(default_factory=list)
                    #publicacion : Publicacion = None
                    #pubEn : publicadoEn = None
                    #keywords : List[str] = dataclasses.field(default_factory=list)
                    "text" : art.text,
                    "oid" : art.oid,
                    "orcid" : art.orcid
                    }
                )

            logging.info ("Result insArticulo: {} - ID: {}".format(result,id))
            # Si se insertó bien y el articulo incluye una lista de autores grabarlos
            if id :
                for autor in art.autores:
                    result_aut, id_aut = self.insAutor(autor)
                    # Despues de grabar el autores grabar la relacion entre articulo y autor
                    if id_aut:
                        result_rel = self.insAutorDe(autor=autor,articulo=art)

            # Si se insertó bien y el articulo incluye una lista de keywords grabarlos
            if id :
                for keyword in art.keywords:
                    result_key, id_key = self.insKeyword(art=art,keyword=keyword)

            # Si se insertó bien y el articulo incluye una lista de articulos de referencia, insertarlos
            if id:
                for artref in art.referencias:
                    result_artref, idart_ref = self.insArticuloReferencia(artref=artref)
                    # Despues de grabar el articulo referenciado, grabar la referencia
                    if idart_ref:
                        result_rel = self.insReferenciaA(art=art,artref=artref)

        else:
            result = self.db.getVertex(classname="Articulo",keys={"titulo":art.titulo})
            id = self.db.extractId(result)
            logging.info ("El Artículo ya existe. ID: {}".format(id))
        return result,id
    
    '''
    Graba un articulo de referencia (resumido) en la base de datos.
    Graba y asocia todas las entidades relacionadas, como ser autores,
    instituciones, keywords, referencias, etc.
    '''
    def insArticuloReferencia (self,artref : ArticuloReferencia) -> Tuple[str,int]:
        if not self.db.existVertex (classname="Articulo",keys={"titulo":artref.titulo}):
            result,id = self.db.insVertex(
                classname="Articulo",
                fields={
                    "titulo" : artref.titulo,
                    #autores : List[Autor] = dataclasses.field(default_factory=list)
                    #publicacion : Publicacion = None
                    #pubEn : publicadoEn = None
                    #keywords : List[str] = dataclasses.field(default_factory=list)
                    "oid" : artref.oid,
                    "orcid" : artref.orcid
                    }
                )

            logging.info ("Result insArticuloReferencia: {} - ID: {}".format(result,id))
            # Si se insertó bien y el articulo incluye una lista de autores grabarlos
            if id :
                for autor in artref.autores:
                    result_aut, id_aut = self.insAutor(autor)
                    # Despues de grabar el autores grabar la relacion entre articulo y autor
                    if id_aut:
                        result_rel = self.insAutorDe(autor=autor,articulo=artref)

        else:
            result = self.db.getVertex(classname="Articulo",keys={"titulo":artref.titulo})
            id = self.db.extractId(result)
            logging.info ("El Artículo ya existe. ID: {}, creando relaciones...".format(id))
            
            # El artículo ya existía, dar de alta la relacion con sus autores
            if id :
                for autor in artref.autores:
                    result_aut, id_aut = self.insAutor(autor)
                    # Despues de grabar el autores grabar la relacion entre articulo y autor
                    if id_aut:
                        result_rel = self.insAutorDe(autor=autor,articulo=artref)

        return result,id

    '''
    Gestión de keywords asociadas a los artículos
    '''
    def insKeyword (self,art : Articulo, keyword : str):
        result = None
        count = 0
        query = "update Articulo SET keywords = keywords||'{keyword}' where (titulo = '{titulo}')".format(titulo=art.titulo,keyword=keyword)
        result = self.db.execCommand(query)
        if result:
            count = self.db.extractCount(result)
            logging.debug ("Insertado KEYWORD: {}. ID: {}".format(keyword,id))
        else:
            count = 0
            logging.debug ("Error al insertar KEYWORD: {}.".format(keyword))
        return result,count

    def delKeyword (self,art : Articulo, keyword : str):
        result = None
        count = 0
        query = "update Articulo REMOVE keywords = '{keyword}' where (titulo = '{titulo}')".format(titulo=art.titulo,keyword=keyword)
        result = self.db.execCommand(query)
        if result:
            count = self.db.extractCount(result)
        else:
            count = 0
        return result,count
    
    '''
    def updConcepto (self,oldConcepto : Concepto,newConcepto : Concepto) -> Tuple[str, int]:
        result = self.db.updVertex(
            classname="Concepto",
            keys={
                "Nombre":oldConcepto.Nombre
            },
            fields={
                "Nombre":newConcepto.Nombre
                }
            )
        if result:
            # El update no devuelve un ID sino la cantidad de registros afectados
            count = self.db.extractCount(result)
        else:
            count = 0
        return result,count

    def delConcepto (self,concepto : Concepto, safe : bool=True) -> Tuple[str,int]:
        result = None
        count = 0
        if safe:
            if not self.isSafeDelete(concepto):
                raise Exception("El concepto tiene relaciones, no es posible eliminarlo")

        result = self.db.delVertex(
            classname="Concepto",
            keys={
                "Nombre":concepto.Nombre
            })
        if result:
            # El delete no devuelve un ID sino la cantidad de registros afectados
            count = self.db.extractCount(result)
        else:
            count = 0
        return result,count

    def isSafeDelete (self, concepto : Concepto) -> bool:
        r = self.getRefsConcepto(concepto)
        return r == 0
        # Probando, porque por algun motivo la linea de abajo cree que es una tupla
        # return bool(refs == 0)

    def getRefsConcepto (self,concepto : Concepto) -> int:
        #
        # La funcion obtiene la cantidad de referencias (entrantes y salientes) de un concepto dado.
        # Si no encuentra el Concepto devuelve 0
        #
        query = "match {{class: Concepto, as: c, where: (Nombre = '{nombre}')}} return (c.in().size()+c.out().size()) as referencias".format(nombre=concepto.Nombre)
        result = self.db.execCommand(query)
        if result:
            referencias = result[0]["referencias"]
            return referencias
        else:
            return 0

    def getConceptos (self, keys : Dict = None, limit : int = 0):
        if keys:
            condicion = self.db.__getWhereFromDict__(keys)
        else:
            condicion = '1=1'
        if limit:
            limite = 'LIMIT {limit}'.format(limit=limit)
        else:
            limite = ''
        query = "match {{class: Concepto, as: c, where: ({condicion})}} return expand(c) as result {limite}".format(condicion=condicion,limite=limite)
        result = self.db.execCommand(query)
        if result:
            return result
        else:
            return None

    def getConceptosComplejos (self):
        result = self.getConceptos()
        complejos = []
        for concepto in result:
            if concepto['Nombre']:
                t = concepto['Nombre'].split()
                if (len(t) > 1):
                    complejos.append(concepto)
        return complejos

    def getConceptoByName (self,name : str):
        return self.getConceptos(keys={"Nombre":name})
    '''

    #--------------------------------------------------------------------------------------------
    # GESTION DE EQUIVALENCIAS
    # --------------------------------------------------------------------------------------------
    '''
    def insEquivalencia (self,concepto : Concepto, equivalencia : str, peso : float):
        result = None
        count = 0
        query = "update Concepto SET Equivalencias['{equivalencia}'] = {peso} where (Nombre = '{nombre}')".format(nombre=concepto.Nombre,equivalencia=equivalencia,peso=peso)
        result = self.db.execCommand(query)
        if result:
            count = self.db.extractCount(result)
        else:
            count = 0
        return result,count
    
    def delEquivalencia (self,concepto : Concepto, equivalencia : str):
        result = None
        count = 0
        query = "update Concepto remove Equivalencias = '{equivalencia}' where (Nombre = '{nombre}')".format(nombre=concepto.Nombre,equivalencia=equivalencia)
        result = self.db.execCommand(query)
        if result:
            count = self.db.extractCount(result)
        else:
            count = 0
        return result,count

    def getEquivalencias (self,concepto : Concepto) -> str:
        query = "match {{class: Concepto, as: c, where: (Nombre = '{nombre}')}} return c.Equivalencias as equivalencias".format(nombre=concepto.Nombre)
        result = self.db.execCommand(query)
        if result:
            equivalencias = result[0]["equivalencias"]
            return equivalencias
        else:
            return None
    '''

    #--------------------------------------------------------------------------------------------
    # GESTION DE AUTORIAS
    # --------------------------------------------------------------------------------------------
    '''
    def insRelacion (self,conceptoOrigen : Concepto, relacion : Relacion, conceptoDestino : Concepto):
        result = self.db.insEdge(
            sourceClass='Concepto',
            sourceCondition={'Nombre':conceptoOrigen.Nombre},
            destClass='Concepto',
            destCondition={'Nombre':conceptoDestino.Nombre},
            edgeClass=relacion.Class
            )
        return result

    #TODO: Falta el método para eliminar una relación
    def delRelacion (self,conceptoOrigen : Concepto, relacion : Relacion, conceptoDestino : Concepto):
        raise NotImplementedError
    
    def isValidRelacionName (self,relacionName : str) -> bool:
        # El nombre de una relacion es valido si es una palabra, sino hay que adecuarlo
        return (len(relacionName.split()) == 1)

    def addTipoRelacion (self,nombreTipo : str):
        result = None
        count = 0
        if not self.isValidRelacionName(nombreTipo):
            raise Exception ("El nombre no es válido para la relación")

        query = "create class {classname} if not exists extends Relacion".format(classname=nombreTipo)
        result = self.db.execCommand(query)
        # La creacion de una clase no devuelve id ni count
        return result,count

    def getRelacionesComplejas (self):
        result = self.getRelaciones()
        complejas = []
        for relacion in result:
            t = re.findall('([A-Z][a-z]+)', relacion['@class'])
            if (len(t) > 1):
                complejas.append(relacion)
        return complejas

    def getRelaciones (self, keys : Dict = None, limit : int = 0):
        if keys:
            condicion = self.db.__getWhereFromDict__(keys)
        else:
            condicion = '1=1'
        if limit:
            limite = 'LIMIT {limit}'.format(limit=limit)
        else:
            limite = ''
        query = "select @class,count(*) as records from Relacion where {condicion} group by @class {limite}".format(condicion=condicion,limite=limite)
        result = self.db.execQuery(query=query)
        return result

    def getRelacionByName (self,name : str):
        # El query utiliza el nombre de la clase para filtrar
        return self.getRelaciones(keys={'@class':name})
    '''

    #--------------------------------------------------------------------------------------------
    # OTRAS OPERACIONES
    # --------------------------------------------------------------------------------------------
    '''
    def getTipoTermino (self,termino : Termino):
        raise NotImplementedError
    
    def cleanTerminos (self,terminos : List) -> List:
        raise NotImplementedError

    def insStruct (self,conceptoOrigen : Concepto, relacion : Relacion, conceptoDestino : Concepto):
        #
        # Inserta una estructura completa C -> R -> C, creando las entidades que no existan
        #
        result = None
        # La posible creacion del tipo de relacion se debe hacer fuera de la transacción sino no funciona
        if not self.existTipoRelacion(tipo = relacion.Class):
            result = self.addTipoRelacion(nombreTipo=relacion.Class)
            if not result:
                return result
        
        script = """
LET concepto_origen = SELECT from Concepto where Nombre = '{origen}'.toUpperCase();
if ($concepto_origen.size() = 0) {{
    LET concepto_origen = CREATE VERTEX Concepto SET Nombre = '{origen}'.toUpperCase();
}}
LET concepto_destino = SELECT from Concepto where Nombre = '{destino}'.toUpperCase();
if ($concepto_destino.size() = 0) {{
    LET concepto_destino = CREATE VERTEX Concepto SET Nombre = '{destino}'.toUpperCase();
}}
LET relacion = match
            {{class:Concepto, as: c1, where: (Nombre.toUpperCase() = '{origen}'.toUpperCase())}}.out('{relacion}') 
            {{class:Concepto, as: c2, where: (Nombre.toUpperCase() = '{destino}'.toUpperCase())}} return a;
if ($relacion.size() = 0) {{
    CREATE EDGE {relacion} FROM $concepto_origen TO $concepto_destino RETRY 100;
}}
"""
        script = script.format(origen=conceptoOrigen.Nombre,relacion=relacion.Class,destino=conceptoDestino.Nombre)
        result = self.db.execBatch(execScript = script)
        return result

    def existStruct (self,conceptoOrigen : Concepto, relacion : Relacion, conceptoDestino : Concepto) -> bool:
        query = "match {{class: Concepto, as: c1, where:(Nombre = '{c1}')}}.out('{r}') " \
                "{{class: Concepto, as: c2, where:(Nombre = '{c2}')}} " \
                "return count(*) as count".format(c1=conceptoOrigen.Nombre,r=relacion.Class,c2=conceptoDestino.Nombre)
        result = self.db.execQuery(query)
        count = result[0]['count']        
        return (count == 1)

    def existConcepto (self,concepto : str) -> bool:
        result = self.getConceptoByName(concepto)
        if result:
            return True
        else:
            return False

    def existTipoRelacion (self,tipo : str) -> bool:
        result = self.getRelacionByName(tipo)
        if result:
            return True
        else:
            return False

    def normalizeTipoRelacion (self,tipo : str) -> str:
        # Capitalizar cada palabra
        pascalcase = tipo.title()
        # Eliminar todo tipo de espacios
        normalized = re.sub(r'\s', '', pascalcase)
        return normalized

    def setClass (self, word : str) -> Tuple[str,str]:
        qryconceptos = "match \
	        {{class: Concepto, as: c, where: (Nombre in ['{word}'])}} \
                return c.Nombre as Nombre, c.@class.toUppercase() as clase".format(word=word)
        resultq = self.db.execQuery(qryconceptos)
        if len(resultq):
            clase = resultq[0]['clase']
            return (word,clase)
        else:
            qryrelaciones = "match \
	            {{class: Relacion, as: r, where: (@class in ['{word}'])}} \
                    return distinct r.@class.toUppercase() as Nombre, 'RELACION' as clase".format(word=word)
            resultr = self.db.execQuery(qryrelaciones)
            if len(resultr):
                clase = resultr[0]['clase']
                return (word,clase)
            else:
                return (word,None)

    def setClasses (self, words : List[str]) -> List[Tuple[str,str]]:
        # Es un diccionario para que la clave sea la palabra y el dato el tipo de item (concepto/relacion)
        classes = dict()

        listIn = self.db.__getInList__(words)
        qryconceptos = "match \
	        {{class: Concepto, as: c, where: (Nombre in [{words}])}} \
                return c.Nombre as Nombre, c.@class.toUppercase() as clase".format(words=listIn)
        resultq = self.db.execQuery(qryconceptos)
        for item in resultq:
            classes[item['Nombre']] = item['clase']

        qryrelaciones = "match \
            {{class: Relacion, as: r, where: (@class in [{words}])}} \
                return distinct r.@class.toUppercase() as Nombre, 'RELACION' as clase".format(words=listIn)
        resultr = self.db.execQuery(qryrelaciones)
        for item in resultr:
            classes[item['Nombre']] = item['clase']
        
        return classes
    '''

    #--------------------------------------------------------------------------------------------
    # CONSULTAS ESPECIFICAS Y METODOS ASOCIADOS
    # --------------------------------------------------------------------------------------------
    '''
    def buildPathQuery (self,conceptoInicial : Concepto, conceptosIncluidos : List) -> str: 
        """Devuelve una ruta a partir de un nodo raiz y una lista de conceptos.
        La funcion recibe un nodo raíz (string) y una lista de conceptos (list(strings)) y
        devuelve el query que al ejecutarse devuelve esos datos.
        Establece una profundidad máxima igual a la cantidad de conceptos relacionados
        para evitar loops infinitos en caso de haber ciclos en la ruta
        Args:
            root (string): Nombre del nodo raiz para iniciar la búsqueda
            concepts (list): Lista de strings con los nombres de los nodos a buscar
        Returns:
            string: JSON con los datos encontrados
        """    
        conceptos = conceptosIncluidos
        conceptos.insert(0,conceptoInicial.Nombre)

        max_len = len(conceptos)
        concept_list = json.dumps(conceptos)
        concept_list = concept_list.replace('"',"'")
        query_route = """select FROM (
        MATCH {{class: Concepto, where: (Nombre = '{root}')}}.out()
            {{class: Concepto, as: dest, 
                while: (
                ($depth < {profundidad}) and 
                (Nombre IN {conceptos_incluidos})
                ),
                where: (
                Nombre IN {conceptos_incluidos}
                )
            }} 
        RETURN 
            DISTINCT 
            dest.@rid as idConcepto,
            dest.Nombre as Concepto,  
            dest.out() as idConceptosRelacionados, 
            dest.outE().@class as Relaciones, 
            dest.out().Nombre as ConceptosRelacionados
        )""".format(root=conceptoInicial.Nombre,profundidad=max_len,conceptos_incluidos=concept_list)
        return query_route

    def buildPathDepth (self,conceptoInicial : Concepto, profundidad : int) -> str:
        """Devuelve un nodo y todas sus relaciones hasta un nivel determinado
        La función recibe un nodo raíz (string) y una profundidad determinada y devuelve
        el query que al ejecutar obtiene esos datos.
        Args:
            root (string): Nombre del nodo raiz para iniciar la búsqueda
            depth (int): Profundidad máxima para la búsqueda de relaciones
        Returns:
            string: JSON con los datos del resultado
        """    
        query_conceptos_depth = """select FROM ( 
        MATCH {{class: Concepto, where: (Nombre = '{root}')}}.out() 
            {{class: Concepto, as: dest, while: ($depth < {profundidad})}} 
        RETURN 
            dest.@rid as idConcepto,
            dest.Nombre as Concepto,  
            dest.out() as idConceptosRelacionados, 
            dest.outE().@class as Relaciones, 
            dest.out().Nombre as ConceptosRelacionados
        )""".format(root=conceptoInicial.Nombre,profundidad=profundidad)
        return query_conceptos_depth
        
    def getPath (self,conceptoInicial : Concepto, conceptosIncluidos : List):
        query = self.buildPathQuery(conceptoInicial=conceptoInicial,conceptosIncluidos=conceptosIncluidos)
        result = self.db.execCommand(command=query)
        return result

    def getPathRespuesta (self,respuesta : Respuesta):
        # TODO: Devolver la ruta correspondiente a los nodos de una respuesta
        pass

    def getPathsFrom (self,conceptoInicial : Concepto, profundidad : int):
        query = self.buildPathDepth(conceptoInicial=conceptoInicial,profundidad=profundidad)
        result = self.db.execCommand(command=query)
        return result

    def getPathsByType (self,relacion : Relacion):
        # TODO: Devuelve todas las rutas, con sus conceptos, de un tipo indicado
        query = "select from Concepto where out('{relname}').size() > 0 or in('{relname}').size() > 0".format(relname=relacion.Class)
        result = self.db.execCommand(query)
        return result
    '''

    #--------------------------------------------------------------------------------------------
    # GESTION DE RESPUESTAS (PUNTAJE EVALUACION ETC)
    # --------------------------------------------------------------------------------------------
    '''
    def tokenizeRespuesta (self, texto : str, textManager : TextManager = None, includeStopWords : bool = False):
        tm = None
        ret_tokens = []
        if textManager:
            tm = textManager
        else:
            tm = TextManager()
        correcciones,tokens = tm.tokenize(texto)
        if not len(correcciones):
            if not includeStopWords:
                words = [ tk['lema'].upper() for tk in tokens if not tk['stop']]
            else:
                words = [ tk['lema'].upper() for tk in tokens]
            clases = self.setClasses(words=words)

            tokens_out = []
            for tk in tokens:
                # Obtener el mapeo, o cadena vacía si no lo hay
                clase = clases.get(tk['lema'].upper(),"")
                claseSugerida = self.mapTipoTermino.get(tk['trans_pos'],"")
                tk['claseDB'] = clase
                tk['claseSugerida'] = claseSugerida
                tokens_out.append(tk)

            if not includeStopWords:
                ret_tokens = [ tk for tk in tokens_out if not tk['stop']]
            else:
                ret_tokens = [ tk for tk in tokens]
        
        return correcciones,ret_tokens
    '''