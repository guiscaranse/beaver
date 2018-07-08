import re
import unicodedata

from bs4 import BeautifulSoup
from ftfy import fix_encoding
from fuzzywuzzy import fuzz

from beaver.config import settings


def normalizeword(palavra: str) -> str:
    """
    Normaliza uma palavra individualmente (remove acento e caracteres especiais)
    :param palavra: palavra a ser normalizada
    :return: palavra normalizada
    """
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    if not palavra.islower() and not palavra.isupper():
        return palavra
    else:
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavra_sem_acento)


def normalize(texto: str) -> str:
    """
    Remove caracteres especiais e acentos da língua portuguesa
    :param texto: texto a ser normalizado
    :return: texto sem caracteres especiais ou acentos
    """
    retorno = ""
    for palavra in str(texto).rsplit(" "):
        retorno += normalizeword(palavra) + " "
    return str(retorno)


def fixcharset(string):
    """
    Tenta consertar uma string em relação a codificação do texto de múltiplas maneiras
    :param string: texto a ser consertado
    :return: texto consertado
    """
    text = fix_encoding(string)
    if "�" in text:
        text = text.encode(settings['replacement_charset'], "ignore")
    return BeautifulSoup(text).get_text()


def relatives_compare_text(relatives: dict, text: str) -> int:
    """
    Compara o texto de uma lista de postagens relativas e da uma média no final
    :rtype: integer
    :param relatives: postagens relativas (pode ser do Bing ou Google) -> Ler gnews_search ou bing_search
    :param text: texto a ser comparado (da postagem original)
    :return: média da pontuação dos textos
    """
    result = 0
    for news in relatives:
        result += fuzz.token_sort_ratio(news['text'], text)
    if len(relatives) > 0:
        return result / len(relatives)
    else:
        return 0
