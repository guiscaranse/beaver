import os
import pendulum
from fuzzywuzzy import fuzz
from py_ms_cognitive import PyMsCognitiveNewsSearch

from beaver.config import settings
from beaver.exceptions import BeaverError
from beaver.post import extract


def search_relatives(query_str):
    """
    Procura no Bing, posts similares com >50 de pontuação no token_sort_ratio limitado a 10 resultados
    :param query_str: conteúdo a ser buscado (Pode ser um título ou o conteúdo da postagem)
    :return: dicionário com um dicionário onde 'relatives' é uma array de dicionários dos dados dos posts similares,
    e 'score' é uma média do token_sort_ratio dos resultados similares.
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
            dados = extract(result.url)
            dados['date'] = pendulum.parse(result.date_published, tz=settings['timezone'])
            rel_response['relatives'].append(dados)
    if meta_score > 0:
        rel_response['score'] = meta_score / len(rel_response['relatives'])
    else:
        rel_response['score'] = meta_score
    return rel_response
