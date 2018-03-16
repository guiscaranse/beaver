import os

import pendulum
from ftfy import fix_encoding
from fuzzywuzzy import fuzz
from goose3 import Goose
from py_ms_cognitive import PyMsCognitiveNewsSearch

from beaver.config import settings
from beaver.exceptions import BeaverError


def fixcharset(string):
    """
    Tenta consertar uma string em relação a codificação do texto de múltiplas maneiras
    :param string: texto a ser consertado
    :return: texto consertado
    """
    text = fix_encoding(string)
    if "�" in text:
        text = text.encode(settings['replacement_charset'], "ignore")
    return text


def extract(url):
    """
    Extrai de uma URL qualquer dados de uma postagem
    :param url: link a ser extraído (necessita ser uma postagem)
    :return: um objeto dicionário com título do artigo, autor, domínio, data e texto do artigo
    Na ausência do texto do artigo irá ser utilizado o resumo presente na meta_description
    """
    g = Goose({'use_meta_language': True, 'target_language': settings['language'].replace("-", "_"),
               'parser_class': 'soup'})
    response = dict()
    artigo = g.extract(url=url)
    response['article_title'] = fixcharset(artigo.title)
    response['author'] = artigo.authors
    response['domain'] = artigo.domain
    if artigo.publish_date is not None:
        response['date'] = pendulum.parse(artigo.publish_date, tz=settings['timezone'])
    else:
        response['date'] = artigo.publish_date
    if len(artigo.cleaned_text) > 0:
        text = fixcharset(artigo.cleaned_text)
    else:
        text = fixcharset(artigo.meta_description)
    response['text'] = text
    return response
