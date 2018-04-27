import os
import sys

import nltk
from logbook import Logger, StreamHandler
from nltk.corpus import stopwords
from polyglot.downloader import downloader
from polyglot.text import Text

from beaver.config import settings
from beaver.util import normalize

if "BEAVER_DEBUG" in os.environ:
    StreamHandler(sys.stdout).push_application()
log = Logger('Lumberjack')


def check_and_download(package):
    if downloader.is_installed(package) == downloader.NOT_INSTALLED:
        log.info(package.split(".")[0] + " não instalado, instalando.")
        check_and_download(package)
        log.info(package.split(".")[0] + " instalado.")
    return True


def verify_polyglot():
    check_and_download("embeddings2.pt")
    check_and_download("pos2.pt")
    check_and_download("ner2.pt")
    check_and_download("sentiment2.pt")


def filter_stopwords(texto):
    try:
        nltk.data.find('corpora\stopwords')
    except LookupError:
        nltk.download('stopwords')
    p_stopwords = set(stopwords.words('portuguese'))
    filtered = (w for w in texto.split() if w.lower() not in p_stopwords)
    return " ".join(filtered)


def gramatica(texto):
    resposta = dict()
    log.info("Verificando tags...")
    log.info("Texto filtrado: " + normalize(texto))
    polyglot_text = Text(texto, hint_language_code=settings['language'][:2])
    for word, tag in polyglot_text.pos_tags:
        if tag in resposta.keys():
            resposta[tag] += 1
        else:
            resposta[tag] = 1
    log.info("Resposta: " + str(resposta))
    return resposta


def polaridade(texto):
    resultado = 0
    polyglot_text = Text(filter_stopwords(texto), hint_language_code=settings['language'][:2])
    for w in polyglot_text.words:
        resultado += w.polarity
    return resultado

