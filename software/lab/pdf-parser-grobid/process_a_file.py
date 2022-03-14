from grobid_client.grobid_client import GrobidClient
import pathlib
import os

print("Inicializando")
client = GrobidClient()

generateIDs = 1
consolidate_header = 1
consolidate_citations = 1
include_raw_citations = 1
include_raw_affiliations = 1
teiCoordinates = 1


pdfs = [    
    "10-121-1-DR.pdf",
    "15-111-1-DR.pdf"    
]

"""
    21-116-1-DR.pdf  28-113-1-DR.pdf  31-128-1-DR.pdf  36-136-2-DR.pdf  39-123-1-DR.pdf  42-129-1-DR.pdf  46-114-1-DR.pdf  53-147-1-DR.pdf  8-133-2-DR.pdf
    11-124-1-DR.pdf  16-117-1-DR.pdf  22-120-1-DR.pdf  29-127-1-DR.pdf  32-135-1-DR.pdf  36-136-3-DR.pdf  40-152-2-DR.pdf  43-130-1-DR.pdf  48-146-1-DR.pdf  54-149-1-DR.pdf  9-115-1-DR.pdf
    12-122-1-DR.pdf  17-150-1-DR.pdf  26-148-1-DR.pdf  30-144-1-DR.pdf  33-143-1-DR.pdf  37-134-1-DR.pdf  41-140-1-DR.pdf  44-139-1-DR.pdf  51-138-1-DR.pdf  60-145-1-DR.pdf
    13-151-1-DR.pdf  18-142-1-DR.pdf  27-131-3-DR.pdf  3-110-1-DR.pdf   34-125-1-DR.pdf  38-112-1-DR.pdf  4-141-1-SP.pdf   45-137-1-DR.pdf  52-126-1-DR.pdf  7-119-1-DR.pdf
"""


for pdf_name in pdfs:
    print("Procesando: " + pdf_name)
    pdf_file, status, text = client.process_pdf("processFulltextDocument", "/home/befede/Informatic/Projects/UTN/utn-scarif/software/lab/pdf-parser/data-papers/"+pdf_name+".pdf", generateIDs, consolidate_header, consolidate_citations, include_raw_citations, include_raw_affiliations, teiCoordinates )
    filename = "./outputs/" + pdf_name + ".tei.xml"
    try:
        soup = BeautifulSoup(text, 'lxml')

        print(soup.title)
        pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
        with open(filename,'w',encoding='utf8') as tei_file:
            tei_file.write(text)
    except OSError:
        print("Writing resulting TEI XML file", filename, "failed")
    # client.process("processFulltextDocument", "/home/befede/Informatic/Projects/UTN/utn-scarif/software/lab/pdf-parser/data-papers", output="./outputs_lightweight/", consolidate_citations=True, teiCoordinates=True, force=True)
print("LISTO")


