import os
import sys

import pendulum
from logbook import Logger, StreamHandler
from polyglot.detect import Detector

import beaver.database
from beaver import post, text_polyglot
from beaver.config import settings
from beaver.exceptions import TimeError, InsufficientText, IncompatibleLanguage
from beaver.search import bing_search, gnews_search
from beaver.util import relatives_compare_text

if "BEAVER_DEBUG" in os.environ:
    StreamHandler(sys.stdout).push_application()
log = Logger('Analyse')


def validate(gooseobject: dict, ignore: bool) -> bool:
    """
    Valida algumas informações da notícia sendo analisada. Reservar esta área para definir regras
    :param gooseobject: objeto beaver.post
    :param ignore: ignorar validações
    """
    # Verifica data
    if gooseobject['date'] is not None:
        diff = pendulum.now() - gooseobject['date']
        if diff.years > 0:
            if not ignore:
                raise TimeError("Artigos com mais de um ano de publicação podem causar análises errôneas e por isso "
                                "não são analisadas")
    return True


def score(url: str, ignore_validations: bool = False, ignore_db: bool = False) -> dict:
    """
    Analisa a pontuação de uma notícia, sendo a pontuação a probabilidade desta ser falsa ou não
    :param ignore_db: Se deve ignorar a existência do banco de dados
    :param ignore_validations: Se deve ignorar validações
    :param url: link a ser analisado
    :return: retorna um dicionário com as respectivas pontuações em cada categoria
    O dicionário é dividido em 'domain' (pontuações do domínio) e 'post' (pontuações da notícia)
    """
    final_score = dict(domain_score={}, post={}, polyglot={})
    postagem = post.extract(url)
    detector = Detector(postagem['text'])
    if detector.language.code not in settings['language']:
        raise IncompatibleLanguage("Língua do artigo não é uma das línguas autorizadas.")
    if not ignore_db:
        if len(beaver.database.checkpost(postagem['article_title'] + postagem['domain'])) > 0:
            log.info("Encontrado correspondência de Domínio em BD")
            objeto = beaver.database.checkpost(postagem['article_title'] + postagem['domain'])
            objeto['domain_score'] = beaver.database.checkdomains(postagem['domain'])
            log.info("Dados: " + str(objeto))
            return objeto

    final_score['polyglot'] = dict(grammar=text_polyglot.gramatica(postagem['text']),
                                   polarity=text_polyglot.polaridade(postagem['text']))
    final_score['other'] = dict(length=0)
    log.info("Analisando '" + postagem['article_title'] + "'")
    log.info("Validando postagem...")
    validate(postagem, ignore_validations)
    log.info("Analisando domínio...")
    final_score['domain_score'] = beaver.database.checkdomains(postagem['domain'])
    log.info("Analisando relatives (BING)...")
    bing_relatives = bing_search.search_relatives(postagem['article_title'], postagem['domain'])
    log.info("Analisando relatives (GOOGLE)...")
    gnews_relatives = gnews_search.search_relatives(postagem['article_title'], postagem['domain'])
    log.info("Analisando multiplicando relatives (BING)...")
    final_score['post']['bing'] = round(float(bing_relatives['score']) / 1, 2)
    log.info("Analisando multiplicando relatives (GOOGLE)...")
    final_score['post']['google'] = round(float(gnews_relatives['score']) / 1, 2)
    if len(str(postagem['text'])) <= 170:
        raise InsufficientText("Texto menor de 170 caracteres é insuficiente de ser analisado. " +
                               postagem['domain'])
    else:
        final_score['other']['length'] = len(str(postagem['text']).rsplit(" "))
    log.info("Comparando textos (BING)...")
    final_score['post']['relatives_bing_text'] = round(
        float(relatives_compare_text(bing_relatives['relatives'], postagem['text'])) / 1, 2)
    log.info("Comparando textos (GOOGLE)...")
    final_score['post']['relatives_google_text'] = round(
        float(relatives_compare_text(gnews_relatives['relatives'], postagem['text'])) / 1, 2)
    final_score['post']['average_score'] = round(sum(final_score['post'].values()) / float(len(final_score['post'])), 2)
    if not ignore_db:
        try:
            beaver.database.registerpost(postagem, final_score)
        except Exception:
            pass
    log.info("Dados: " + str(final_score))
    return final_score
