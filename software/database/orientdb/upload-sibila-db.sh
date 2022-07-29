#!/bin/bash

# Copia todos los archivos de la base de datos PPR a la instancia remota de Amazon
rsync -avzLP -e "ssh -i ~/data/orientdb/base-aws-key-pair.pem" \
       ~/data/orientdb/databases/PPR/* \
       ec2-user@18.229.177.23:~/data/orientdb/databases/PPR

rsync -avzLP -e "ssh -i ~/data/orientdb/base-aws-key-pair.pem" \
	~/data/orientdb/databases/sibila-patterns/* \
	ec2-user@18.229.177.23:~/data/orientdb/databases/sibila-patterns


