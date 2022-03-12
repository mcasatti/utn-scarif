import io
from pdfminer.converter import TextConverter, HTMLConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.high_level import extract_pages
from io import StringIO
import json
import os
from PyPDF2 import PdfFileReader


class PdfParser:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def get_info(self):
        info = ""
        with open(self.pdf_path, 'rb') as fh:
            pdf = PdfFileReader(fh)
            info = pdf.getDocumentInfo()
        return info

    def extract_text_by_page(self):
        with open(self.pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(
                    resource_manager, converter)
                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                yield text
                # close open handles
                converter.close()
                fake_file_handle.close()

    def get_pages(self):
        pages = extract_pages(self.pdf_path)
        return pages

    def convert_pdf_to_text(self, pages=None):
        if not pages:
            page_nums = set()
        else:
            page_nums = set(pages)

        output = StringIO()
        manager = PDFResourceManager()
        converter = TextConverter(
            manager, output, laparams=LAParams(boxes_flow=1))
        interpreter = PDFPageInterpreter(manager, converter)

        pdf_file = open(self.pdf_path, 'rb')
        for page in PDFPage.get_pages(pdf_file, page_nums):
            interpreter.process_page(page)
        pdf_file.close()
        converter.close()
        text = output.getvalue()
        output.close
        return text

    def convert_pdf_to_html(self):
        resource_manager = PDFResourceManager()
        buffer_str = io.BytesIO()
        codec = 'utf-8'
        laparams = LAParams(boxes_flow=1, line_margin=0.7)
        converter = HTMLConverter(
            resource_manager, buffer_str,  laparams=laparams)
        file_pdf = open(self.pdf_path, 'rb')
        interpreter = PDFPageInterpreter(resource_manager, converter)
        password = ""
        maxpages = 0  # is for all
        caching = True
        pagenos = set()
        for page in PDFPage.get_pages(file_pdf, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
            interpreter.process_page(page)
        file_pdf.close()
        converter.close()
        output_html = buffer_str.getvalue()
        buffer_str.close()
        return output_html

    def export_as_json(self, json_path):
        filename = os.path.splitext(os.path.basename(self.pdf_path))[0]
        data = {'Filename': filename}
        data['Pages'] = []
        counter = 1
        for page in self.extract_text_by_page(self.pdf_path):
            text = page
            page = {'Page_{}'.format(counter): text}
            data['Pages'].append(page)
            counter += 1
        with open(json_path, 'w') as fh:
            json.dump(data, fh)
