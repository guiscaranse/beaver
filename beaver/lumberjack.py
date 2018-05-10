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


def check_and_download(package: str) -> bool:
    """
    Verifica se determinado pacote do Polyglot está instalado, caso não, será instalado automaticamente
    :param package: pacote a ser procurado
    :return: Verdadeiro sempre. Se houverem erros uma excessão será levantada
    """
    if downloader.is_installed(package) == downloader.NOT_INSTALLED:
        log.info(package.split(".")[0] + " não instalado, instalando.")
        check_and_download(package)
        log.info(package.split(".")[0] + " instalado.")
    return True


def verify_polyglot():
    """
    Verifica se os pacotes que este programa usa estão instalados
    """
    check_and_download("embeddings2.pt")
    check_and_download("pos2.pt")
    check_and_download("ner2.pt")
    check_and_download("sentiment2.pt")


def filter_stopwords(texto: str) -> str:
    """
    Filtra stopwords, removendo-as
    :param texto: Texto a ser filtrado
    :return: Texto filtrado
    """
    try:
        nltk.data.find('corpora\stopwords')
    except LookupError:
        nltk.download('stopwords')
    if len(texto) == 0:
        log.info("Não existe texto")
        return ""
    p_stopwords = set(stopwords.words('portuguese'))
    filtered = (w for w in texto.split() if w.lower() not in p_stopwords)
    return " ".join(filtered)


def gramatica(texto: str) -> dict:
    """
    Analisa e conta cada token de um texto no formato explicado aqui: http://polyglot.readthedocs.io/en/latest/POS.html
    :param texto: Texto a ser analisado
    :return: Dicionário com as tags presentes e a quantia delas
    """
    resposta = dict()
    log.info("Verificando tags...")
    if len(texto) == 0:
        log.info("Não existe texto")
        return dict()
    log.info("Texto filtrado: " + normalize(texto))
    polyglot_text = Text(texto, hint_language_code=settings['language'][:2])
    for word, tag in polyglot_text.pos_tags:
        if tag in resposta.keys():
            resposta[tag] += 1
        else:
            resposta[tag] = 1
    # Porcentagem
    total = sum(resposta.values())
    log.info("Total de Gramática: " + str(total))
    for tag in resposta.keys():
        resposta[tag] = round(resposta[tag]/total, 3)
    log.info("Resposta: " + str(resposta))
    return resposta


def polaridade(texto: str) -> dict:
    """
    Verifica a polaridade de um texto (sentimentos bons/ruins)
    :param texto: Texto a ser analisado
    :return: Polaridade em número
    """
    resultado = dict(good=0, bad=0)
    if len(texto) == 0:
        log.info("Não existe texto")
        return resultado
    polyglot_text = Text(filter_stopwords(texto), hint_language_code=settings['language'][:2])
    for w in polyglot_text.words:
        pol = w.polarity
        if pol < 0:
            resultado['bad'] += 1
        elif pol > 0:
            resultado['good'] += 1
    resultado['bad'] = resultado['bad']/len(polyglot_text.words)
    resultado['good'] = resultado['good'] / len(polyglot_text.words)
    return resultado

