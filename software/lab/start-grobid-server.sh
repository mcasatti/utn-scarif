#!/bin/bash

docker run -t --rm --init --name grobid -p 8070:8070 lfoppiano/grobid:0.7.0 
