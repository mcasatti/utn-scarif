# print("Inicializando")
# client = GrobidClient()
# client.process("processFulltextDocument", "/home/befede/Informatic/Projects/UTN/utn-scarif/software/lab/pdf-parser/data-papers", output="./outputs_lightweith/", consolidate_citations=True, teiCoordinates=True, force=True)
# print("LISTO")

from grobid_client.grobid_client import GrobidClient
import pathlib
import os
from bs4 import BeautifulSoup

from TEIFile import TEIFile
import pandas as pd

papers_csv = []

print("Inicializando")
client = GrobidClient(config_path="./config.json")

generateIDs = 1
consolidate_header = 1
consolidate_citations = 1
include_raw_citations = 1
include_raw_affiliations = 1
teiCoordinates = 1


pdfs = [     
    "13-151-1-DR",
    "17-150-1-DR",
    "40-152-2-DR",
    # "10-121-1-DR",
    # "53-147-1-DR",
    # "22-120-1-DR",
    # "52-126-1-DR",
    # "26-148-1-DR",
    # "46-114-1-DR",
    # "/4-141-1-SP",
    # "/8-133-2-DR",
    # "51-138-1-DR",
    # "60-145-1-DR",
    # "11-124-1-DR",
    # "48-146-1-DR",
    # "21-116-1-DR",
    # "/3-110-1-DR",
    # "42-129-1-DR",
    # "15-111-1-DR",
    # "27-131-3-DR",
    # "12-122-1-DR",
    # "37-134-1-DR",
    # "41-140-1-DR",
    # "16-117-1-DR",
    # "34-125-1-DR",
    # "31-128-1-DR",
    # "/7-119-1-DR",
    # "28-113-1-DR",
    # "38-112-1-DR",
    # "29-127-1-DR",
    # "30-144-1-DR",
    # "54-149-1-DR",
    # "/9-115-1-DR",
    # "44-139-1-DR",
    # "45-137-1-DR",
    # "32-135-1-DR",
    # "36-136-2-DR",
    # "36-136-3-DR",
    # "39-123-1-DR",
    # "43-130-1-DR",
    # "18-142-1-DR",
    # "33-143-1-DR"
]

def tei_to_csv_entry(tei_file):
    tei = TEIFile(tei_file)    
    base_name = tei_file[0:-8] 
    return base_name, tei.doi, tei.title, len(tei.authors),len(tei.references)


for pdf_name in pdfs:
    print("Procesando: " + pdf_name)
    pdf_file, status, text = client.process_pdf("processFulltextDocument", "../data-papers/"+pdf_name+".pdf", 1, generateIDs, consolidate_header, consolidate_citations, include_raw_citations, include_raw_affiliations, teiCoordinates )
    filename = "./outputs/" + pdf_name + ".tei.xml"
    try:
        # soup = BeautifulSoup(text, 'lxml')
        # title = soup.title.getText()
        # abstract = soup.abstract.getText(separator=' ', strip=True)
        pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
        with open(filename,'w',encoding='utf8') as tei_file:
            tei_file.write(text)        
    except OSError:
        print("Writing resulting TEI XML file", filename, "failed")



for pdf_name in pdfs:
    print("Procesando: " + pdf_name)
    # pdf_file, status, text = client.process_pdf("processFulltextDocument", "/home/befede/Informatic/Projects/UTN/utn-scarif/software/lab/pdf-parser/data-papers/"+pdf_name+".pdf", generateIDs, consolidate_header, consolidate_citations, include_raw_citations, include_raw_affiliations, teiCoordinates )
    filename = "./outputs/" + pdf_name + ".tei.xml"
    try:
        papers_csv.append(tei_to_csv_entry(filename))
    except OSError:
        print("Writing resulting TEI XML file", filename, "failed")

result_csv = pd.DataFrame(papers_csv, columns=['ID', 'DOI','Title', 'Cantidad de autores', 'Referencias'])
result_csv.to_csv("summary_papers.csv", index=False)

# tei = TEIFile(filename)
        
    # client.process("processFulltextDocument", "/home/befede/Informatic/Projects/UTN/utn-scarif/software/lab/pdf-parser/data-papers", output="./outputs_lightweight/", consolidate_citations=True, teiCoordinates=True, force=True)
print("LISTO")


