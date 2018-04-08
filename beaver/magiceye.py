import os
import sys

from halo import Halo

from beaver.analyse import score
from beaver.config import score_table
from beaver.post import extract


def magic(url):
    with Halo(text='Analisando noticias... Isto pode levar um tempo', spinner='dots') as halo:
        try:
            # Desativa uns erros de encoding chatos
            sys.stdout = os.devnull
            sys.stderr = os.devnull
            postagem = extract(url)['article_title']
            halo.succeed("Detectado postagem: " + postagem)
            halo.start("Extraindo e analisando dados...")
            pontuacao = score(url)
            halo.succeed("Terminado análise, computando pontuação...")
            if score_table['tc'] <= float(pontuacao['truth_score']) < score_table['safe']:
                halo.warn("Esta notícia é segura mas possivelmente tendenciosa! E obteve pontuação " +
                          str(round(pontuacao['truth_score'], 2)))
            elif float(pontuacao['truth_score']) < score_table['tc']:
                halo.fail("Esta notícia foi marcada como falsa, tendenciosa ou clickbait. E obteve pontuação " +
                          str(round(pontuacao['truth_score'], 2)))
            else:
                halo.succeed("Esta notícia foi marcada como segura. E possui pontuação " +
                             str(round(pontuacao['truth_score'], 2)))
        except Exception as e:
            halo.fail("Ocorreu um erro e não foi possível continuar (Erro: " + str(e) + ")")
