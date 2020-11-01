import tika
from tika import parser
import json

tika.TikaClientOnly = True

#file = '/home/mcasatti/data/scarif/data-papers/10-121-1-DR.pdf'
#file = '/home/mcasatti/data/scarif/data-papers/12-122-1-DR.pdf'
file = '/home/mcasatti/data/scarif/data-papers/17-150-1-DR.pdf'
#file = '/home/mcasatti/data/scarif/data-papers/paper-jein-2019.docx'
#file = '/home/mcasatti/data/scarif/data-papers/patrones.doc'
#file = '/home/mcasatti/data/scarif/data-papers/caedi.docx'
# Parse data from file
file_data = parser.from_file(file,xmlContent=True)
# Get files text content
text = file_data['content']
print(text)
#meta = file_data['metadata']
#print(json.dumps(meta,indent=4))
