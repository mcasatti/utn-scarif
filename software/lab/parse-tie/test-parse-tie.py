from itertools import count
from typing import Dict
from bs4 import BeautifulSoup
import os
import glob
from rich import print, inspect
from rich.syntax import Syntax
import time
import json
import logging
from scarifentities import Articulo, ArticuloReferencia, Autor, Institucion, Publicacion, publicadoEn
from rich.logging import RichHandler
from pydantic.json import pydantic_encoder
from cienciomanager import CiencioManager
import sys

def parse_articulo (soup):
    title = soup.filedesc.titlestmt.title.text.replace("?","\?");
    logging.debug("Titulo articulo: {}".format(title))
    articulo = Articulo(titulo=title)
    autores = parse_autores(soup)
    articulo.autores = autores
    publicacion,pubEn = parse_publicacion(soup)
    articulo.publicacion = publicacion
    articulo.pubEn = pubEn
    keywords = parse_keywords(soup)
    articulo.keywords = keywords
    articulo.text = parse_body(soup)
    articulo.referencias = parse_referencias(soup)
    return articulo

def parse_autores (soup):
    logging.debug("Obteniendo los autores...")
    sourceDesc = soup.find("sourcedesc")
    auth = sourceDesc.find_all("author")
    logging.debug("Cantidad de autores: {}".format(len(auth)))
    autores = []
    for author in auth:
        ape_text = ""
        nom1_text = ""
        nom2_text = ""
        mail_text = ""

        apellido = author.surname
        if apellido:
            ape_text = apellido.text

        nombre1 = author.find(name="forename",attrs={"type" : "first"})
        if nombre1:
            nom1_text = nombre1.text

        nombre2 = author.find(name="forename",attrs={"type" : "middle"})
        if nombre2:
            nom2_text = nombre2.text

        mail = author.find(name="email")
        if mail:
            mail_text = mail.text

        nom = "{apellido}, {nombre} {medio}".format(apellido=ape_text,nombre=nom1_text,medio=nom2_text)
        autor = Autor(nombre = nom,email = mail_text)
        logging.debug(autor)
        instituciones = parse_instituciones_author(author)    
        autor.instituciones = instituciones

        autores.append(autor)  
        
    return autores  

def parse_instituciones_author (author):
    logging.debug("Parseando instituciones...")
    insts = author.find_all (name="orgname")
    insts_data = []
    for inst in insts:
        inst_text = inst.text
        inst_type = inst["type"]
        inst = Institucion(nombre=inst_text,tipo=inst_type)
        logging.debug (inst)
        insts_data.append(inst)
    return insts_data

def parse_publicacion (soup):
    logging.debug("Parseando publicación...")
    if soup.publicationstmt:
        logging.debug ("PUBLICACION: {}".format(soup.publicationstmt))
        if soup.publicationstmt.publisher:
            public = soup.publicationstmt.publisher.text
        else:
            public = None
        if soup.publicationstmt.date:
            fecha = soup.publicationstmt.date.text
            if fecha == "":
                fecha = None
        else:
            fecha = None
    oid = soup.find("idno",attrs={"type" : "DOI"})
    oid_text = None
    if oid:
        oid_text = oid.text
    publicacion = Publicacion(titulo=public)
    pubEn = publicadoEn(fecha=fecha,publicacion=publicacion,oid=oid_text)
    logging.debug(publicacion)
    logging.debug(pubEn)
    return publicacion,pubEn

def parse_keywords (soup):
    logging.debug("Parseando keywords...")
    kw = soup.find("keywords")
    keywords = []
    if kw:
        terms = kw.find_all("term")
        if terms:
            for term in terms:
                logging.debug("Termino: {}".format(term.text))
                keywords.append(term.text)
    return keywords

def parse_body (soup):
    logging.debug("Parseando body...")
    bdy = soup.find("body")
    text = ""
    if bdy:
        divs = bdy.find_all("div",{"xmlns" : "http://www.tei-c.org/ns/1.0"})
        logging.debug("DIVS CANT:{}".format(len(divs)))
        if divs:
            for div in divs:
                txt_aux = None
                if div.contents:
                    txt_aux = " {} ".format(div.contents[0])
                    ps = div.find_all("p")
                    if ps:
                        for p in ps:
                            txt_aux = "{}{}".format(txt_aux,p.text).replace('"','').replace("'",'')
                    logging.debug (txt_aux)
                    text = text + txt_aux
                
    return text  

def parse_referencias (soup):
    logging.debug("Parseando referencias bibliograficas...")
    biblio = soup.find("listbibl")
    articulos = []
    if biblio:
        biblios = biblio.find_all("biblstruct")
        if biblios:
            for bib in biblios:
                analytic = bib.find("analytic")
                if analytic:
                    logging.debug ("ANALYTIC: {}".format(analytic))
                    if analytic.title:
                        titulo = analytic.title.text
                        articulo = ArticuloReferencia(titulo=titulo)
                        autores = []
                        logging.debug("Titulo: {}".format(titulo))
                        auth = analytic.find_all("author")
                        logging.debug("Cantidad de autores: {}".format(len(auth)))
                        autores = []
                        for author in auth:
                            ape_text = ""
                            nom1_text = ""
                            nom2_text = ""
                            mail_text = ""

                            apellido = author.surname
                            if apellido:
                                ape_text = apellido.text

                            nombre1 = author.find(name="forename",attrs={"type" : "first"})
                            if nombre1:
                                nom1_text = nombre1.text

                            nombre2 = author.find(name="forename",attrs={"type" : "middle"})
                            if nombre2:
                                nom2_text = nombre2.text

                            mail = author.find(name="email")
                            if mail:
                                mail_text = mail.text

                            nom = "{apellido}, {nombre} {medio}".format(apellido=ape_text,nombre=nom1_text,medio=nom2_text)
                            autor = Autor(nombre = nom,email = mail_text)
                            autores.append(autor)
                            logging.debug(autor)
                        articulo.autores = autores
                        idno = analytic.idno
                        #logging.debug ("IDNO: {}".format(idno))
                        if idno and idno.has_attr('type'):
                            if idno["type"] == "DOI":
                                articulo.oid = idno.text
                            elif idno["type"] == "ORCID":
                                articulo.orcid = idno.text
                        articulos.append(articulo)
    logging.debug ("REFERENCIAS: {}".format(articulos))
    return articulos      

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger().error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def main ():
    FORMAT = "%(asctime)s [%(levelname)s] %(message)s" # "%(message)s"
    #logging.basicConfig(level=logging.INFO,handlers=[RichHandler()])
    logging.basicConfig(
        level=logging.ERROR, format=FORMAT, datefmt="[%X]", 
        handlers=[
            RichHandler(),
            logging.FileHandler("debug.log",mode='w')
        ]
    )

    #logging.getLogger().setLevel(logging.DEBUG)

    cm = CiencioManager()

    print(os.getcwd())
    print(__file__)
    home = os.path.dirname(__file__)
    datafolder = os.path.join(home,'xml/')
    dirname = os.path.join(datafolder, '*.xml')
    print (dirname)
    files = glob.glob(dirname)
    
    
    #files = [
    # "/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/7-119-1-DR.tei.xml",
    # "/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/11-124-1-DR.tei.xml",
    # "/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/16-117-1-DR.tei.xml",
    # "/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/12-122-1-DR.tei.xml",
    # "/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/43-130-1-DR.tei.xml",
    #"/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/42-129-1-DR.tei.xml",       # Signos de pregunta
    #"/home/mcasatti/utn/investigacion/utn-scarif/software/lab/parse-tie/xml/10-121-1-DR.tei.xml",        # Signos de pregunta (no detecta titulo)
    #]
    
    

    start_total = time.time()
    cant_archivos = 0
    for file in files:
        try:
            cant_archivos += 1
            #print ("="*80)
            #print ("File: {}".format(file))
            #print ("Iniciando procesamiento de TEI")

            tei_doc = file
            with open(tei_doc, 'r') as tei:
                soup = BeautifulSoup(tei, 'lxml')

                #syntax = Syntax(soup.prettify(), "xml",
                #                theme="material", line_numbers=True)
                #print(syntax, '\n')

                start = time.time()
                articulo = parse_articulo(soup)
                logging.info("Resultado final:")
                logging.info(articulo)
                duration = time.time()-start
                #print (f"Parseo completo en {duration:.3f}s")
                #print ("Grabación de datos de Articulo")

                
                
                start = time.time()
                cm.insArticulo (articulo)
                duration = time.time()-start
                #print (f"Grabación completa en {duration:.3f}s")
                
                '''
                articulo_json = json.dumps(articulo, indent=3, default=pydantic_encoder)
                syntax = Syntax(str(articulo_json), "json", theme="material", line_numbers=True)
                print (syntax)
                '''
        except Exception as e:
            logging.critical(e)
        finally:
            pass

    duration_total = time.time()-start_total
    print ("*"*80)
    print (f"Duración completa del proceso: {duration_total:.3f}s")
    print (f"Cantidad de archivos procesados: {cant_archivos:.0f}")
    tiempo_medio = duration_total / cant_archivos
    print (f"Tiempo medio de proceso (por archivo): {tiempo_medio:.2f}s")
    print ("*"*80)


# Install exception handler
sys.excepthook = handle_exception

if __name__ == "__main__":
    main()

