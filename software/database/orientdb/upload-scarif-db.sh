#!/bin/bash

# Copia todos los archivos de la base de datos utn-scarif a la instancia remota de Amazon
rsync -avzLP -e "ssh -i ~/data/orientdb/base-aws-key-pair.pem" \
       ~/data/orientdb/databases/utn-scarif/* \
       ec2-user@18.229.177.23:~/data/orientdb/databases/utn-scarif


