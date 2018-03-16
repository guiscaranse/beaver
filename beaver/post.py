import os

from ftfy import fix_encoding
from fuzzywuzzy import fuzz
from goose3 import Goose
from py_ms_cognitive import PyMsCognitiveNewsSearch

from beaver.exceptions import BeaverError

settings = dict({'language': "pt-BR", "replacement_charset": "latin1"})


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
    response['date'] = artigo.publish_date
    if len(artigo.cleaned_text) > 0:
        text = fixcharset(artigo.cleaned_text)
    else:
        text = fixcharset(artigo.meta_description)
    response['text'] = text
    return response


def search_relatives(query_str):
    """
    Procura no Bing, posts similares com >50 de pontuação no token_sort_ratio limitado a 10 resultados
    :param query_str: conteúdo a ser buscado (Pode ser um título ou o conteúdo da postagem)
    :return: dicionário com um dicionário onde 'relatives' é uma array dos dados dos posts similares, e 'score' é uma
    média do token_sort_ratio dos resultados similares.
    """
    rel_response = dict(relatives=[])
    meta_score = 0
    if "MS_BING_KEY" not in os.environ:
        raise BeaverError("Chaves da Microsoft devem estar presentes na variável do sistema MS_BING_KEY")
    try:
        results = PyMsCognitiveNewsSearch(os.environ.get("MS_BING_KEY"), query_str, custom_params={
            "mkt": settings['language'], "setLang": settings['language'][:2]}).search(limit=10, format='json')
    except Exception:
        raise BeaverError("Não foi possível se comunicar com o Bing, talvez as chaves tenham expirado?")
    for result in results:
        if fuzz.token_sort_ratio(query_str, result.name) > 50:
            meta_score += fuzz.token_sort_ratio(query_str, result.name)
            rel_response['relatives'].append(extract(result.url))
    if meta_score > 0:
        rel_response['score'] = meta_score / len(rel_response['relatives'])
    else:
        rel_response['score'] = meta_score
    return rel_response
