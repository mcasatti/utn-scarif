from typing import Dict
from bs4 import BeautifulSoup
import os
import glob
from rich import print,inspect

print (os.getcwd())
print (__file__)
dirname = os.path.dirname(__file__)
dirname = os.path.join(dirname,'xml/*.*')
files = glob.glob(dirname)


for file in files:
    
    tei_doc = file
    with open(tei_doc, 'r') as tei:
        soup = BeautifulSoup(tei, 'lxml')
        print (soup.title.text)
        tags = set([tag.name for tag in soup.find_all()])
        print (tags)
        print("\n")
