import hashlib

from tinydb import TinyDB, Query
from tinydb.operations import add

from beaver.config import score_table

db = TinyDB('db.json')


def checkdomains(domain: str) -> dict:
    """
    Verifica se domínio já foi analisado e se sim, retorna a pontuação dele
    :param domain: domínio a ser procurado
    :return: dicionário de pontuação {'domain', 'score_td', 'score_safe', 'score_unsafe'}
    """
    table_domain = db.table('domains')
    query = Query()
    if len(table_domain.search(query.domain == domain)) == 0:
        table_domain.insert({'domain': domain, 'score_td': 0, 'score_safe': 0, 'score_unsafe': 0})
        return dict({'domain': domain, 'score_td': 0, 'score_safe': 0, 'score_unsafe': 0})
    else:
        objeto = table_domain.search(query.domain == domain)[0]
        return objeto


def checkpost(title_domain: str) -> dict:
    """
    Verifica se o post já foi analisado antigamente, se sim retorna pontuação.
    :param title_domain: Título do artigo + Domínio (para hash)
    :return: dicionário contendo o score ou nada
    dict -> {'bing', 'google', 'popular_bing', 'popular_google', 'truth_score'}, 'hash'}
    """
    table = db.table('posts')
    query = Query()
    hashtitle = hashlib.md5(str(title_domain).encode('utf-8')).hexdigest()
    if len(table.search(query.hash == hashtitle)) > 0:
        objeto = table.search(query.hash == hashtitle)[0]
        return objeto
    return dict()


def registerpost(gooseobject: dict, scoredict: dict) -> None:
    """
    Registra uma postagem nova não analisada anteriormente
    :param gooseobject: Objeto beaver.post
    :param scoredict: Dicionário beaver.analyse.score
    """
    table_domain = db.table('domains')
    query = Query()
    scoredict['hash'] = hashlib.md5(str(gooseobject['article_title'] + gooseobject['domain']).encode('utf-8')).hexdigest()
    table = db.table('posts')
    table.insert(scoredict)
    if score_table['tc'] <= float(scoredict['post']['truth_score']) < score_table['safe']:
        # Tendenciosa/Modificada
        table_domain.update(add('score_td', +10), query.domain == gooseobject['domain'])
    elif float(scoredict['post']['truth_score']) < score_table['tc']:
        # Falsa
        table_domain.update(add('score_unsafe', +10), query.domain == gooseobject['domain'])
    else:
        # Segura
        table_domain.update(add('score_safe', +10), query.domain == gooseobject['domain'])
