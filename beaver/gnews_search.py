import json
import urllib.parse
import urllib.request

import pendulum
from fuzzywuzzy import fuzz

from beaver.config import settings
from beaver.post import extract


def search_relatives(string):
    """
    Pesquisa as notícias no feed do Google news, o feed passa por uma API que converte RSS para JSON
    Um exemplo de request retornada pode ser visto aqui: https://pastebin.com/Ef1yseg1
    :param string: texto a ser procurado no google news
    :return: notícias em formato padrão
    """
    meta_score = 0
    gnews_results = dict(relatives=[])
    feed = "https://news.google.com/news/rss/search/section/q/" + urllib.parse.quote_plus(string) + "/" + \
           urllib.parse.quote_plus(string) + "?hl=" + settings['language'] + "&gl=" + settings['country'] + "&ned=" + \
           settings['language'] + "_" + settings['country'].lower()

    json_data = "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote_plus(feed)
    with urllib.request.urlopen(json_data) as url:
        data = json.loads(url.read().decode())
        for item in data['items']:
            if fuzz.token_sort_ratio(string, item['title']) > 50:
                meta_score += fuzz.token_sort_ratio(string, item['title'])
                try:  # Em caso de erros do Goose, não são relevantes quais (Variam de 404 e 500)
                    dados = extract(item['link'])
                    dados['date'] = pendulum.parse(item['pubDate'], tz=settings['timezone'])
                    gnews_results['relatives'].append(dados)
                except Exception:
                    pass
    if meta_score > 0:
        gnews_results['score'] = meta_score / len(gnews_results['relatives'])
    else:
        gnews_results['score'] = meta_score
    return gnews_results
