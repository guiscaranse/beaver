import os
import sys

import nltk
import pendulum
from logbook import Logger, StreamHandler
from nltk.corpus import stopwords

import beaver.database
from beaver import post, text_polyglot
from beaver.search import bing_search, gnews_search
from beaver.config import settings, weights
from beaver.exceptions import TimeError
from beaver.util import relatives_compare_text

if "BEAVER_DEBUG" in os.environ:
    StreamHandler(sys.stdout).push_application()
log = Logger('Analyse')


def validate(gooseobject: beaver.post, ignore: bool) -> bool:
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
                raise TimeError("Artigos de mais de um ano podem causar análises errôneas, digite --help para saber "
                                "como forçar análise.")
    return True


def alltext_score(all_text: str) -> list:
    """
    Esta função analisa a escrita de um texto utilizando o NLTK, permitindo obter palavras-chave de um texto. Após isso
    ele busca algumas palavras chaves formando frases nos veículos de notícias e extraindo a pontuação deles.
    :param all_text: Texto a ser analisado
    :return: Frase "popular" em formato de lista
    """
    try:
        nltk.data.find('corpora\stopwords')
    except LookupError:
        nltk.download('stopwords')
    p_stopwords = set(stopwords.words('portuguese'))
    fd = nltk.FreqDist(w.lower() for w in all_text.split() if w not in p_stopwords)
    max_words = settings['max_words_precision']
    if len(list(fd.keys())) >= settings['max_words_precision']:
        for x in range(0, settings['max_words_precision']):
            max_words = x
        return list(fd.keys())[:max_words]
    else:
        for y in range(0, len(list(fd.keys()))):
            max_words = y
        return list(fd.keys())[:max_words]


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
    if not ignore_db:
        if len(beaver.database.checkpost(postagem['article_title'] + postagem['domain'])) > 0:
            log.info("Encontrado correspondência de Domínio em BD")
            objeto = beaver.database.checkpost(postagem['article_title'] + postagem['domain'])
            objeto['domain_score'] = beaver.database.checkdomains(postagem['domain'])
            return objeto

    final_score['polyglot'] = dict(grammar=text_polyglot.gramatica(postagem['text']),
                                   polarity=text_polyglot.polaridade(postagem['text']))
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
    final_score['post']['bing'] = bing_relatives['score'] * weights['bing']
    log.info("Analisando multiplicando relatives (GOOGLE)...")
    final_score['post']['google'] = gnews_relatives['score'] * weights['google']
    all_text = ""
    log.info("Pegando alltext...")
    for news in bing_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text']))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass
    '''for news in gnews_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text']))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass'''
    log.info("Juntando alltext...")
    popular_words = ' '.join(alltext_score(all_text)).replace(",", "")
    log.info("Popular Words: " + popular_words)
    log.info("Buscando popular words (BING)...")
    final_score['post']['relatives_bing_text'] = relatives_compare_text(bing_relatives['relatives'], postagem['text'])
    log.info("Buscando popular words (GOOGLE)...")
    final_score['post']['relatives_google_text'] = relatives_compare_text(gnews_relatives['relatives'],
                                                                          postagem['text'])
    if len(popular_words) > 0:
        popular_words_gnews_relatives = gnews_search.search_relatives(popular_words, postagem['domain'])['score']
        popular_words_bing_relatives = bing_search.search_relatives(popular_words, postagem['domain'])['score']
        final_score['post']['popular_bing'] = popular_words_bing_relatives * weights['popular_bing']
        final_score['post']['popular_google'] = popular_words_gnews_relatives * weights['popular_google']
    else:
        final_score['post']['popular_bing'] = 0
        final_score['post']['popular_google'] = 0
    final_score['post']['average_score'] = sum(final_score['post'].values()) / float(len(final_score['post']))
    if not ignore_db:
        try:
            beaver.database.registerpost(postagem, final_score)
        except Exception:
            pass
    return final_score
