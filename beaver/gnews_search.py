import urllib.parse
import urllib.request
import json


from beaver.config import settings


def search(string):
    """
    Pesquisa as notícias no feed do Google news, o feed passa por uma API que converte RSS para JSON
    Um exemplo de request retornada pode ser visto aqui: https://pastebin.com/Ef1yseg1
    :param string: texto a ser procurado no google news
    :return: notícias em formato de json (https://pastebin.com/Ef1yseg1)
    """
    feed = "https://news.google.com/news/rss/search/section/q/" + urllib.parse.quote_plus(string) + "/" + \
           urllib.parse.quote_plus(string) + "?hl=" + settings['language'] + "&gl=" + settings['country'] + "&ned=" + \
           settings['language'] + "_" + settings['country'].lower()

    json_data = "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote_plus(feed)
    with urllib.request.urlopen(json_data) as url:
        data = json.loads(url.read().decode())
        return data['items']
