#!/bin/bash

docker run --rm -d --name orientdb -p 2424:2424 -p 2480:2480 \
    -v /home/mcasatti/data/orientdb/databases:/orientdb/databases \
    -e ORIENTDB_ROOT_PASSWORD=kymosadmin117 \
    orientdb
