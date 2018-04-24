import nltk
import pendulum
from nltk.corpus import stopwords

import beaver.database
from beaver import post, bing_search, gnews_search
from beaver.config import settings, weights
from beaver.exceptions import TimeError


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
            if "," in list(fd)[x]:
                break
            max_words = x
        return list(fd.keys())[:max_words]
    else:
        for y in range(0, len(list(fd.keys()))):
            if "," in list(fd)[y]:
                break
            max_words = y
        return list(fd.keys())[:max_words]


def score(url: str, ignore: bool = False, force_db: bool = False) -> dict:
    """
    Analisa a pontuação de uma notícia, sendo a pontuação a probabilidade desta ser falsa ou não
    :param force_db: Se deve ignorar a existência do banco de dados
    :param ignore: Se deve ignorar validações
    :param url: link a ser analisado
    :return: retorna um dicionário com as respectivas pontuações em cada categoria
    O dicionário é dividido em 'domain' (pontuações do domínio) e 'post' (pontuações da notícia)
    """
    final_score = dict(domain_score={}, post={})
    postagem = post.extract(url)
    if not ignore:
        if len(beaver.database.checkpost(postagem['article_title'] + postagem['domain'])):
            objeto = beaver.database.checkpost(postagem['article_title'] + postagem['domain'])
            objeto['domain_score'] = beaver.database.checkdomains(postagem['domain'])
            return objeto
    validate(postagem, ignore)
    final_score['domain_score'] = beaver.database.checkdomains(postagem['domain'])
    bing_relatives = bing_search.search_relatives(postagem['article_title'])
    gnews_relatives = gnews_search.search_relatives(postagem['article_title'], postagem['domain'])
    final_score['post']['bing'] = bing_relatives['score'] * weights['bing']
    final_score['post']['google'] = gnews_relatives['score'] * weights['google']
    all_text = ""
    for news in bing_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text']))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass
    for news in gnews_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text']))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass
    popular_words = ' '.join(alltext_score(all_text))
    if len(popular_words) > 0:
        popular_words_gnews_relatives = gnews_search.search_relatives(popular_words, postagem['domain'])['score']
        popular_words_bing_relatives = bing_search.search_relatives(popular_words, postagem['domain'])['score']
        final_score['post']['popular_bing'] = popular_words_bing_relatives * weights['popular_bing']
        final_score['post']['popular_google'] = popular_words_gnews_relatives * weights['popular_google']
    else:
        final_score['post']['popular_bing'] = 0
        final_score['post']['popular_google'] = 0
    final_score['post']['truth_score'] = sum(final_score['post'].values()) / float(len(final_score['post']))
    if not ignore:
        beaver.database.registerpost(postagem, final_score)
    return final_score
