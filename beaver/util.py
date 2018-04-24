import re
import unicodedata

from ftfy import fix_encoding

from beaver.config import settings


def normalizeword(palavra):
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    if not palavra.islower() and not palavra.isupper():
        return palavra
    else:
        return re.sub('[^a-zA-Z0-9 \\\]', '', palavra_sem_acento)


def normalize(texto):
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
    return text
