#!/bin/bash

# Crear un backup de la base de datos remota (completa) en el directorio backup

# Crear la carpeta temp, para descargar los archivos desde la instancia de Amazon
mkdir -p temp

# Descargar en esa carpeta la carpeta databases remota
# scp -i./base-aws-key-pair.pem -r ec2-user@18.229.177.23:~/data/orientdb/databases/ temp/databases/
rsync -avzpL -e "ssh -i ~/data/orientdb/base-aws-key-pair.pem" \
       ec2-user@18.229.177.23:~/data/orientdb/databases/* \
       ~/data/orientdb/temp/databases

# Crear la carpeta backup, para generar el backup comprimido
mkdir -p backup

# Comprimir la carpeta databases entera en un archivo tar.gz con fecha y hora como nombre
DATE=$(date +%Y-%m-%d-%H%M%S)
BACKUP_DIR="./backup"
tar -czpf $BACKUP_DIR/backup-$DATE.tar.gz -C temp databases

# Eliminar la carpeta temp con su contenido
rm -r temp