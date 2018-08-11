import os
import socket
import sys
import urllib
from http.client import RemoteDisconnected

import pendulum
from logbook import Logger, StreamHandler
from newsplease import NewsPlease
from polyglot.detect import Detector

from beaver.config import settings
from beaver.exceptions import NoTextDataFound, IncompatibleLanguage
from beaver.util import fixcharset

if "BEAVER_DEBUG" in os.environ:
    StreamHandler(sys.stdout).push_application()
log = Logger('PostExtract')


def extract(url):
    """
    Extrai de uma URL qualquer dados de uma postagem
    :param url: link a ser extraído (necessita ser uma postagem)
    :return: um objeto dicionário com título do artigo, autor, domínio, data e texto do artigo
    Na ausência do texto do artigo irá ser utilizado o resumo presente na meta_description
    """
    log.info("Tetando extrair " + str(url))
    response = dict()
    try:
        artigo = NewsPlease.from_url(url, timeout=5)
        response['article_title'] = fixcharset(artigo.title)
        response['author'] = artigo.authors
        response['domain'] = artigo.source_domain
        if artigo.date_publish is not None:
            response['date'] = pendulum.parse(str(artigo.date_publish).replace(" ", "T"), tz=settings['timezone'])
        elif artigo.date_modify is not None and artigo.date_modify is not "None":
            response['date'] = pendulum.parse(str(artigo.date_modify).replace(" ", "T"), tz=settings['timezone'])
        else:
            response['date'] = pendulum.parse(str(artigo.date_download).replace(" ", "T"), tz=settings['timezone'])
        if artigo.text is not None:
            text = fixcharset(artigo.text)
        elif artigo.description is not None:
            text = fixcharset(artigo.description)
        else:
            raise NoTextDataFound("Não existem textos disponíveis no NewsPlease para análise. Tente com Goose3")
        response['text'] = text
        log.info("Sucesso (news-please)")
    except (RemoteDisconnected, NoTextDataFound, socket.timeout, ConnectionResetError, urllib.error.HTTPError,
            urllib.error.URLError):
        # Falhou, tentando com o Goose3
        log.error("News-Please falhou, tentando Goose3")
        from goose3 import Goose
        g = Goose({'strict': False, 'use_meta_language': True, 'target_language': settings['language'].replace("-", "_"),
                   'parser_class': 'lxml', 'enable_image_fetching': False})
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
        elif len(artigo.meta_description) > 0:
            text = fixcharset(artigo.meta_description)
        else:
            raise NoTextDataFound("Não existem textos suficientes para análise.")
        response['text'] = text
        log.info("Sucesso (Goose3)")
        pass
    detector = Detector(response['text'])
    if detector.language.code not in settings['language']:
        raise IncompatibleLanguage("Língua do artigo não é uma das línguas autorizadas.")
    return response
