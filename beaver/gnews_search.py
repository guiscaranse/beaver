import json
import urllib.parse
import urllib.request

import pendulum
from fuzzywuzzy import fuzz

from beaver.config import settings
from beaver.post import extract


def search_relatives(string, ignore_url=""):
    """
    Pesquisa as notícias no feed do Google news, o feed passa por uma API que converte RSS para JSON
    Um exemplo de request retornada pode ser visto aqui: https://pastebin.com/Ef1yseg1
    :param ignore_url: URL para ignorar notícias
    :param string: texto a ser procurado no google news
    :return: notícias em formato padrão
    """
    meta_score = 0
    gnews_results = dict(relatives=[])
    feed = "https://news.google.com/news/rss/search/section/q/" + urllib.parse.quote_plus(string) + "/" + \
           urllib.parse.quote_plus(string) + "?hl=" + settings['language'] + "&gl=" + settings['country'] + "&ned=" + \
           settings['language'] + "_" + settings['country'].lower()

    json_data = "https://noderssserver-gcakilmtyk.now.sh/?feedURL=" + urllib.parse.quote_plus(feed)
    with urllib.request.urlopen(json_data) as url:
        data = json.loads(url.read().decode())
        if "items" in data:
            for item in data['items']:
                try:
                    dados = None
                    if fuzz.token_sort_ratio(string, item['title']) > 50:
                        if 'link' in item.keys():
                            if ignore_url in item['link']:
                                raise IndexError("URL Inválida")
                            dados = extract(item['link'])
                        elif 'url' in item.keys():
                            if ignore_url in item['url']:
                                raise IndexError("URL Inválida")
                            dados = extract(item['url'])
                        else:
                            raise IndexError("URL não encontrada")
                        if 'pubDate' in item.keys():
                            dados['date'] = pendulum.parse(item['pubDate'], tz=settings['timezone'])
                        elif 'created' in item.keys():
                            dados['date'] = pendulum.parse(item['created'], tz=settings['timezone'])
                        else:
                            dados['date'] = None
                except Exception:
                    pass
                finally:
                    if dados is not None:
                        gnews_results['relatives'].append(dados)
                        meta_score += fuzz.token_sort_ratio(string, item['title'])
    if meta_score > 0:
        gnews_results['score'] = meta_score / len(gnews_results['relatives'])
    else:
        gnews_results['score'] = meta_score
    return gnews_results
