import os

from fuzzywuzzy import fuzz
from goose3 import Goose
from py_ms_cognitive import PyMsCognitiveNewsSearch
from ftfy import fix_encoding

from beaver.exceptions import BeaverError

settings = dict({'language': "pt-BR"})


def extract(url):
    g = Goose({'use_meta_language': True, 'target_language': settings['language'].replace("-", "_"), 'parser_class': 'soup'})
    print("Buscando: ", url)
    response = dict()
    artigo = g.extract(url=url)
    response['article_title'] = artigo.title
    response['author'] = artigo.authors
    response['domain'] = artigo.domain
    response['date'] = artigo.publish_date
    if len(artigo.cleaned_text) > 0:
        text = fix_encoding(artigo.cleaned_text)
        if "�" in text:
            text = text.encode('latin-1', "ignore")
    else:
        text = fix_encoding(artigo.meta_description)
        if "�" in text:
            text = text.encode('latin-1', "ignore")
    response['text'] = text
    print(response)
    return response


def search_relatives(query_str):
    if "MS_BING_KEY" not in os.environ:
        raise BeaverError("Chaves da Microsoft devem estar presentes na variável do sistema MS_BING_KEY")
    try:
        results = PyMsCognitiveNewsSearch(os.environ.get("MS_BING_KEY"), query_str, custom_params={
            "mkt": settings['language'], "setLang": settings['language'][:2]}).search(limit=10, format='json')
    except Exception:
        raise BeaverError("Não foi possível se comunicar com o Bing, talvez as chaves tenham expirado?")
    response = dict(relatives=[])
    for result in results:
        if fuzz.token_sort_ratio(query_str, result.name) > 50:
            response['relatives'].append(extract(result.url))
    return response
