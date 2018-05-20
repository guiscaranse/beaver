import json
import os
import sys
import urllib.parse
import urllib.request

import pendulum
from fuzzywuzzy import fuzz
from logbook import Logger, StreamHandler

from beaver.config import settings
from beaver.post import extract
from beaver.util import normalize

if "BEAVER_DEBUG" in os.environ:
    StreamHandler(sys.stdout).push_application()
log = Logger('GoogleNews')


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
    log.info("Iniciando pesquisa no Google News...")
    json_data = "https://beavergnewsserver.now.sh/search/" + urllib.parse.quote_plus(normalize(string)) + \
                "?lang=" + settings['language']
    log.info("Tentando acessar: " + json_data)
    with urllib.request.urlopen(json_data) as url:
        log.info("Acessado!")
        data = json.loads(url.read().decode())
        if "articles" in data:
            log.info("Encontrado correspondências no Google News. Itens: " + str(len(data['articles'])))
            log.info(str(data))
            for item in data['articles']:
                try:
                    dados = None
                    log.info("Encontrado " + item['title'] + ". Token sort: " +
                             str(fuzz.token_sort_ratio(string, item['title'])))
                    if fuzz.token_sort_ratio(string, item['title']) >= 40:
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
                        log.info("Extraído URL. Dados: " + str(item))
                        if 'pubDate' in item.keys():
                            try:
                                dados['date'] = pendulum.parse(item['pubDate'], tz=settings['timezone'])
                            except Exception:
                                log.warning("Testando UNIX timestamp para " + str(item['pubDate']))
                                try:
                                    dados['date'] = pendulum.parse(pendulum.from_timestamp(item['pubDate'],
                                                                                           settings['timezone'])
                                                                   .to_iso8601_string(), tz=settings['timezone'])
                                except OSError: # Timestamp está em milissegundos
                                    dados['date'] = pendulum.parse(pendulum.from_timestamp(float(
                                        item['pubDate']/1000.0), settings['timezone']).to_iso8601_string(),
                                                                   tz=settings['timezone'])
                        elif 'created' in item.keys():
                            try:
                                dados['date'] = pendulum.parse(item['created'], tz=settings['timezone'])
                            except Exception:
                                log.warning("Testando UNIX timestamp para " + str(item['created']))
                                try:
                                    dados['date'] = pendulum.parse(pendulum.from_timestamp(item['created'],
                                                                                           settings['timezone'])
                                                                   .to_iso8601_string(), tz=settings['timezone'])
                                except OSError: # Timestamp está em milissegundos
                                    dados['date'] = pendulum.parse(pendulum.from_timestamp(float(
                                        item['created']/1000.0), settings['timezone']).to_iso8601_string(),
                                                                   tz=settings['timezone'])
                        else:
                            dados['date'] = None
                except Exception as e:
                    log.error("Erro: " + str(e))
                    pass
                finally:
                    log.info("Nenhum erro, inserindo.")
                    if dados is not None:
                        log.info("Inserindo: " + str(dados))
                        gnews_results['relatives'].append(dados)
                        meta_score += fuzz.token_sort_ratio(string, item['title'])
    if meta_score > 0:
        gnews_results['score'] = meta_score / len(gnews_results['relatives'])
    else:
        gnews_results['score'] = meta_score
    return gnews_results
