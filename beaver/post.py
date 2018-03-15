import os

from goose3 import Goose
from py_ms_cognitive import PyMsCognitiveNewsSearch
from fuzzywuzzy import fuzz, process

from beaver.exceptions import BeaverError

settings = dict({'language': "pt-BR", 'country': "BR"})


def extract(url):
    g = Goose({'use_meta_language': True, 'target_language': settings['language'], 'parser_class': 'soup'})
    response = dict()
    artigo = g.extract(url=url)
    response['article_title'] = artigo.title
    response['author'] = artigo.authors
    response['domain'] = artigo.domain
    response['date'] = artigo.publish_date
    if len(artigo.cleaned_text) > 0:
        response['text'] = artigo.cleaned_text
    else:
        response['text'] = artigo.meta_description
    return response


def search_relatives(query_str):
    print("Buscando por:", query_str)
    if "MS_BING_KEY" not in os.environ:
        raise BeaverError("Chaves da Microsoft devem estar presentes na variável do sistema MS_BING_KEY")
    try:
        results = PyMsCognitiveNewsSearch(os.environ.get("MS_BING_KEY"), query_str, custom_params={
            "mkt": settings['language'], "setLang": "pt"}).search(limit=10, format='json')
    except Exception:
        raise BeaverError("Não foi possível se comunicar com o Bing, talvez as chaves tenham expirado?")
    for result in results:
        print(result.name)
        print(result.description)
        print("Analisando: ", result.name)
        print("Token_sort:", fuzz.token_sort_ratio(query_str, result.name))
        print("Token__set:", fuzz.token_set_ratio(query_str, result.name))
        print("ratio:", fuzz.ratio(query_str, result.name))
        print("partial_ratio:", fuzz.partial_ratio(query_str, result.name))
        print("\n")
