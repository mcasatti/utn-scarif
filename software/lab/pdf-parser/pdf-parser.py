#Importar el módulo de manejo de PDF
import PyPDF2

# creating a pdf file object
pdfFileObj = open('./data-papers/3-110-1-DR.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
pdfDocInfo = pdfReader.documentInfo


# printing number of pages in pdf file
print("NumPages:", pdfReader.numPages)
print("Author:", pdfDocInfo.author)
print("Creator:", pdfDocInfo.creator)
print("Subject:", pdfDocInfo.subject)
print("Title:", pdfDocInfo.title)

print(pdfDocInfo)

# exit()

# creating a page object
text = ""
for page in range(pdfReader.numPages):
     pageObj = pdfReader.getPage(page)
     text += pageObj.extractText()
#
# # extracting text from page
print(text)
#
# # closing the pdf file object
pdfFileObj.close()
#
