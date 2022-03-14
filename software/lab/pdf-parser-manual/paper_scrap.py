
from io import StringIO
from bs4 import BeautifulSoup
import re
import json
import os


class PaperScrap():


     def __init__(self, text_html="", text=""):
          self.text_html = text_html
          self.text = text
          self.referencies = {
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

     def set_text_html(self, text_html):
          self.text_html = text_html

     def get_titles(self):
          """
               Extrae los títulos del pdf jerarquizados según el tamaño de letra
          """
          soup = BeautifulSoup(self.text_html, "html.parser")
          max_font_size = 50
          titles = dict()
          for i in range(50):
               regex_title = r'font-size:' + str(i+1) + 'px'
               results = soup.findAll("span", attrs={'style':re.compile(regex_title)})
               if results:
                    titles_element = []
                    for result in results:
                         style = {}
                         style_str = result.get("style")                    
                         for sty in style_str.split(";"):
                              attr = sty.split(":")[0]
                              value = sty.split(":")[1]
                              style.update({attr: value})

                         titles_element.append({
                              "text": result.text,
                              "style": style
                         })
                    titles.update({i+1:titles_element})
          
          return titles

     
     def get_title(self):
          """
               Extrae el título del paper. Asume que el título es el texto con mayor tamano de letra
          """
          soup = BeautifulSoup(self.text_html, "html.parser")
          font_size = self.get_fonts_size()[-1]                    
          regex_title = r'font-size:' + str(font_size) + 'px'
          results = soup.findAll("span", attrs={'style':re.compile(regex_title)})
          title = ""          
          if results:               
               for result in results:
                    # print(result.parent.get("style"))
                    title += result.text.replace("\n", "")            
          return title

     def get_authors(self):
          """
               Extrae los autores del paper asumiendo que están después del título y antes del abstract
          """
          regex_university = ".*[Universidad|Facultad|Departamento|universidad|facultad|departamento]*."
          regex_mail = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

          # Tamano de letra de titulo
          font_size = self.get_fonts_size()[-1]               
          title_detected = False   
          abstract_detected = False  
          university_detexted = False                  
          soup = BeautifulSoup(self.text_html, "html.parser")      
          results = soup.findAll("span")   
          
          academic_data_text = ""
          
          font_size_author = ""

          for r in results:
               if ("font-size:" + str(font_size) + 'px') in r.get("style"):
                    title_detected = True
                    continue


               if title_detected:                                        
                    if "Resumen" in r.text or "RESUMEN" in r.text or "cid:70" in r.text:
                         break               
               

               font_size_author = font_size
               academic_data_text += r.text

               if re.match(regex_university,r.text):        
                    university_detected = True
                                   
          academic_data_array = academic_data_text.split("\n\n")
          authors = []
          emails = []
          university = ""

          for academic_data in academic_data_array:                                             
               
               text_to_match = academic_data               
               for email in re.findall(regex_mail,text_to_match):
                    if email:
                         emails.append(email)               
               
               
               if re.match(regex_university,text_to_match):                    
                    university += academic_data.replace("\n", "")
               else:                    
                    if academic_data:
                         for author in academic_data.split(","):                              
                              authors.append(author.replace("\n", ""))

               # Borramos todo lo que este despues del ultimo mail en institucion
               if emails:
                    last_email = emails[-1]
                    index_last_email = university.find(last_email)
                    university = university[0:index_last_email+len(last_email)]
               
          return authors, emails, university

     def get_abstract(self):   
          soup = BeautifulSoup(self.text_html, "html.parser")      
          results = soup.findAll("span")          
          font_size_abstract_title = ""
          font_size_abstract_body = ""
          element_abstract_title = ""
          anstract_detected = False
          abstract_text = ""

          for result in results:
               if result.text.find("Resumen") > -1:
                    element_abstract_title = result
                    font_size_abstract_title = self.get_font_size(element_abstract_title)
                    anstract_detected = True
                    continue
                    # break
                              
               if anstract_detected:
                    if self.get_font_size(result) < font_size_abstract_title:
                         if result.text != "":
                              abstract_text += result.text 
                    else:
                         break
 
          
          return abstract_text.replace("\n", "")

     def get_referencies(self):         
          # Tamano de letra de titulo
          
          """
          referencies_detected = False            
          index_referencies = self.text.lower().find('referencias')          
          referencias_str = self.text[index_referencies+len("referencias"):]
          referencias_array = []
          for ref in referencias_str.split("\n\n") :
               referencias_array.append(ref.replace("\n",""))
          return referencias_array
          """
          soup = BeautifulSoup(self.text_html, "html.parser")      
          results = soup.findAll("span")
          
          font_size_referencies_title = ""
          font_size_referencies_body = ""
          element_reference_title = ""

          referencies_detected = False
          referencies_text = ""
          for result in results:
               if result.text.find("Referencia") > -1:
                    element_reference_title = result
                    font_size_referencies_title = self.get_font_size(element_reference_title)
                    referencies_detected = True
                    continue
                    # break
               referencies = []
               
               if referencies_detected:

                    if self.get_font_size(result) < font_size_referencies_title:
                         if result.text != "":
                              # print(result)
                              # print("----------")
                              referencies_text += result.text
                              # print(result.text)
                              # referencies.append(result.text)
                    else:
                         break
 
          
          return referencies_text
          


     def get_font_size(self, element):
          try:
               style_str = element.get("style")         
                         
               for sty in style_str.split(";"):
                    attr = sty.split(":")[0]
                    value = sty.split(":")[1]
                    if attr.find("font-size") > -1:
                         return value
          except:
               return ""
          return ""

     def get_text_with_style(self, text):
          soup = BeautifulSoup(self.text_html, "html.parser")
          
          spans = soup.findAll("span")          
          results = []
          
          if spans:
               for span in spans:                    
                    if span.text.replace("\n", "") == text:
                         style_str = span.get("style")     
                         style = {}               
                         for sty in style_str.split(";"):
                              attr = sty.split(":")[0]
                              value = sty.split(":")[1]
                              style.update({attr: value})

                         results.append(style)
          return results


     def get_styles(self, referencies=None):
          if not referencies:
               referencies = self.referencies

          styles = {}
          for ref in referencies:
               styles.update({referencies[ref]: self.get_text_with_style(referencies[ref])}) 
          
          return styles

     def get_fonts_size(self):    
          soup = BeautifulSoup(self.text_html, "html.parser")
          max_font_size = 100
          fonts_size = []
          for i in range(max_font_size):
               regex_title = r'font-size:' + str(i+1) + 'px'
               results = soup.findAll("span", attrs={'style':re.compile(regex_title)})
               if results:
                    fonts_size.append(i+1)                    
          return fonts_size


     def get_text_by_font_size(self, font_size):
          soup = BeautifulSoup(self.text_html, "html.parser")     
          text = []
          regex_title = r'font-size:' + str(font_size) + 'px'
          results = soup.findAll("span", attrs={'style':re.compile(regex_title)})
          if results:                    
               for result in results:                                             
                    text.append(result.text.replace("\n", ""))               
          return text

     def get_boxes(self):
          """
               Extrae los títulos del pdf jerarquizados según el tamaño de letra
          """
          soup = BeautifulSoup(self.text_html, "html.parser")
          boxes = []
          titles = dict()

          regex_title = r'border: textbox'
          results = soup.findAll("div", attrs={'style':re.compile(regex_title)})
          if results:                              
               for result in results:
                    boxes.append(result)                         
          return boxes

     def get_sections(self, font_size):     
          soup = BeautifulSoup(self.text_html, "html.parser")     
          sections = []
          regex = re.compile(r'font-size:+' + str(font_size) + 'px')
          results = soup.findAll("span")

          if results:                    
               section = None
               last_section = None
               index = -1
               for result in results:  
                    text = result.text.replace("\n","")
                    if not text:
                         continue
                    if regex.findall(str(result)):
                         # Si matchea es porque es titulo
                         title =  text
                         if last_section == "title":                      
                              sections[index]['title'] += title
                         else:
                              # es nueva seccion                         
                              index += 1
                              sections.append({"title": title, "content": ""})     
                         last_section = "title"
                    else:
                         try:
                              sections[index]['content'] += text
                         except:
                              sections.append({"title": "", "content": text})
                              index += 1
                         last_section = "content"
                         
                    # sections.append(result.text)
                    # print(result.findAll("span"))
                    # print(str())
                    
          return sections
                   

#def get_keywords(text_html):
#     soup = BeautifulSoup(text_html, "html.parser")     
#     results = soup.findAll(re.compile(r'^Palabra<.+>clave'))