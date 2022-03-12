# PDF parser manual

Laboratorio para realizar pruebas en la obtención de información académica a partir de un paper en formato pdf.

Para la extracción del texto del pdf se utiliza [pdfminer](https://pypi.org/project/pdfminer/). Documentación [aquí](https://pdfminersix.readthedocs.io/_/downloads/en/develop/pdf/)

Para el análisis del texto y la obtención de información se llevan a cabo diversas estrategias que van desde el análisis de la fuente y tamaño de letra como también el uso de expresiones regulares.

## Instalación
- Se recomienda crear un entorno virtual para manejar las dependencias (opcional)
- Instalar dependencias: `pip install -r requirements.txt`

## Uso
- Parseo de documentos
  - __Html__ -> `python3 main.py -a generate_html -f <ruta_archivo_pdf>`
  - __Texto__ -> `  python3 main.py -a generate_txt -f <ruta_archivo_pdf>  `
- Análisis de un documento en particular -> `python3 main.py -f <ruta_archivo_pdf>`
- Análisis de todos los documentos de un directorio -> `python3 main.py -d <ruta_directorio>`