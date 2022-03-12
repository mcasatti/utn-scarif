import spacy
from spacy.lang.en.examples import sentences
import es_core_news_sm
import random

print(spacy.__version__)
#nlp = spacy.load("en_core_web_sm")
nlp = es_core_news_sm.load()

for sent in sentences:
    print(sent)
# doc = nlp(sentences[random.randrange(10)])
# print(doc.text)
# for token in doc:
#     print(token.text, token.pos_, token.dep_)

