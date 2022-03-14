from pdf_parser import PdfParser
from paper_scrap import PaperScrap
import argparse
import os
import sys
import six
from termcolor import colored
from pyfiglet import figlet_format

referencies = {
    "abstract": "Resumen",
    "introduction": "Introducción",
    "authors": "Nombre(s) de Autor(es) y filiaciones institucionales",
    "title": "Título Principal",
    "text": "Texto Principal",
    "tables": "Pie de Figuras y Tablas",
    "pictures": "Pie de Figuras y Tablas",
    "heading_1": "Títulos de Primer Nivel",
    "heading_2": "Títulos de Segundo Nivel",
    "heading_3": "Encabezados de Tercer Nivel",
    "footer_notes": "Notas al Pie de Página",
    "gratitude": "Agradecimientos",
    "referencies": "Referencias"

}


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            six.print_(colored(string, color))
        else:
            six.print_(colored(figlet_format(
                string, font=font), color))
    else:
        six.print_(string)


if __name__ == '__main__':
    # main(sys.argv[1])

    log("Scarif", color="blue", figlet=True)
    log("Herramienta de extracción de información de papers ", color="green")

    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", "-f", help="Ruta del archivo pdf")
    parser.add_argument("--directory-path", "-d",
                        help="Ruta del directorio pdf")
    parser.add_argument(
        "--action", "-a", help="Opciones=generate_html, generate_txt")

    args = parser.parse_args()

    file_path = args.file_path
    directory_path = args.directory_path
    action = args.action

    if action == "generate_html":
        if not file_path:
            print("Para generar el html debe especificar el archivo")
            sys.exit()
        pdf_parser = PdfParser(file_path)
        pdf_html = pdf_parser.convert_pdf_to_html()
        print(pdf_html)

    elif action == "generate_txt":
        if not file_path:
            print("Para generar el txt debe especificar el archivo")
            sys.exit()
        pdf_parser = PdfParser(file_path)
        pdf_html = pdf_parser.convert_pdf_to_text()
        print(pdf_html)

    else:
        files_paths = []
        if file_path:
            files_paths.append(file_path)
        if directory_path:
            for entry in os.scandir(directory_path):
                if entry.path.endswith(".pdf") and entry.is_file():
                    files_paths.append(entry.path)
        if not files_paths:
            print("No se ha especificado ningun pdf a analizar")
            sys.exit()

        for file_path in files_paths:
            pdf_parser = PdfParser(file_path)
            pdf_html = pdf_parser.convert_pdf_to_html()
            pdf_text = pdf_parser.convert_pdf_to_text()
            # print(pdf_text)
            paper_scrap = PaperScrap(pdf_html, pdf_text)

            print("\n\n")
            log(file_path, "blue")
            log("\nMetadatos", "green")
            metadatos = pdf_parser.get_info()
            try:
                for metadato in metadatos:
                    print(metadato.replace("/", "") +
                          ": " + metadatos[metadato])
            except:
                print(metadatos)

            log("\nDatos", "green")
            print("Título: " + paper_scrap.get_title())
            authors, emails, university = paper_scrap.get_authors()
            print("Autores: ")
            for author in authors:
                print("\t" + author)
            print("Emails: ")
            for email in emails:
                print("\t" + email)
            print("\nInstitución: " + university)
            abstract = paper_scrap.get_abstract()
            print("\nResumen: ")
            print(abstract)
            referencias = paper_scrap.get_referencies()
            print("\nReferencias: ")
            print(referencias.split("\n"))

    """pdf_text = pdf_parser.convert_pdf_to_text()    



    styles = paper_scrap.get_styles(referencies)

    for style in styles:
        print(style)
        print(styles[style ])
        print("----")
    """

    # Obtenemos el formato del template

    """
    font_sizes = sorted(get_fonts_size(pdf_html), reverse=True)
    for font_size in font_sizes:
        sections = get_sections(pdf_html, font_size)
        print("-------------------------------------------------------")
        print("-------------------------------------------------------")
        print("Asumiendo que los titulos son de tamaño {}".format(str(font_size)))
        print("-------------------------------------------------------")
        print("-------------------------------------------------------")
        print("-------------------------------------------------------")
        for section in sections:          
            print(section['title'])          
            print()
            print(section['content'])
            print()
            print()
    """

    # print(text_html)
    # extract_text(pdf_path)
    """ 
     titles = get_titles(pdf_html)

     level = 1
     print("-----------TEXTO DEL PDF------------\n\n")
     
     for key in sorted(titles, reverse=True):
          print("\n\n--------------------------------------") 
          print("Texto de nivel {}".format(level))
          print("--------------------------------------")
          print("Tamaño letra: {}px\n".format(key))          
          
          for title in titles[key]:
               title_style = title.get("style")
               # print("Estilo:")
               # print(title_style)
               # title = title.get("text").replace("\n", "")
               # if title.replace(" ", "") != "" and not re.compile(r'\d.').match(title):
               print(title.get("text"))                    
          level += 1

     page_total = 0
     for page in get_pages(pdf_path):
          page_total += 1

     
     # print("Cantidad de páginas: {}".format(page_total))

     # print(export_as_json(pdf_path, "./prueba.json"))   

     
     # print(get_sections(text_html))

     # boxes = get_boxes(text_html)

     #for box in boxes:
     #     print(box.text)
     #     print()
    """
