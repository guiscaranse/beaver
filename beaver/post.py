import pendulum
from newsplease import NewsPlease

from beaver.config import settings
from beaver.util import fixcharset


def extract(url):
    """
    Extrai de uma URL qualquer dados de uma postagem
    :param url: link a ser extraído (necessita ser uma postagem)
    :return: um objeto dicionário com título do artigo, autor, domínio, data e texto do artigo
    Na ausência do texto do artigo irá ser utilizado o resumo presente na meta_description
    """
    response = dict()
    artigo = NewsPlease.from_url(url)
    response['article_title'] = fixcharset(artigo.title)
    response['author'] = artigo.authors
    response['domain'] = artigo.source_domain
    if artigo.date_publish is not None:
        response['date'] = pendulum.parse(str(artigo.date_publish).replace(" ", "T"), tz=settings['timezone'])
    else:
        response['date'] = str(artigo.date_download).replace(" ", "T")
    if len(artigo.text) > 0:
        text = fixcharset(artigo.text)
    else:
        text = fixcharset(artigo.description)
    response['text'] = text
    return response
