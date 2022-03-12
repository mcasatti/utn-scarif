# Prueba de uso de Grobid 

- Correr servidor GROBID
```
docker run -t --rm --init -p 8080:8070 -p 8081:8071 grobid/grobid:0.6.2
```
- Instalar dependencias del proyecto 
```
pip install -r requirements.txt
git clone https://github.com/kermitt2/grobid_client_python
cd grobid_client_python
python setup.py install

```
- Correr script main.py
```
python3 main.py
```

Los documentos a analizar están definidos en el código, dentro de main.py.

### Funcionamiento
- El script hacae una request al servidor de GROBID para realizar un análisi
- GROOBID retorna un archivo con formato tei.xml los cuales son guardados en el direcotrio outputs
- Se genera un archivo csv con los metadatos de cada documento analizado

### Dependencias
- Cliente grobid https://github.com/kermitt2/grobid_client_python