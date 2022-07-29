#!/bin/bash

# Copia todos los archivos de la base de datos portico a la instancia remota de Amazon
# scp -i./base-aws-key-pair.pem -pr ./databases/portico ec2-user@18.229.177.23:~/data/orientdb/databases/portico

rsync -avzLP --delete -e "ssh -i ~/data/orientdb/base-aws-key-pair.pem" \
       ~/data/orientdb/databases/portico/* \
       ec2-user@18.229.177.23:~/data/orientdb/databases/portico
