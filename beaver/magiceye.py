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
            # Pontuação do domínio
            if pontuacao['domain_score']['score_safe'] == 0 and pontuacao['domain_score']['score_td'] == 0 and \
                    pontuacao['domain_score']['score_unsafe'] == 0:
                halo.info("Este domínio não foi analisado anteriormente.")
            elif pontuacao['domain_score']['score_safe'] < float(pontuacao['domain_score']['score_td']) > \
                    pontuacao['domain']['score_unsafe']:
                halo.warn("Este veículo é seguro mas possivelmente tendenciosa! Pontuação de notícias tendenciosas: " +
                          str(round(pontuacao['domain_score']['score_td'], 2)))
            elif pontuacao['domain_score']['score_td'] < float(pontuacao['domain_score']['score_unsafe']) > \
                    pontuacao['domain_score']['score_safe']:
                halo.fail("Este veículo costuma disseminar notícias falsas! Pontuação de notícias falsas: " +
                          str(round(pontuacao['domain_score']['score_unsafe'], 2)))
            else:
                halo.succeed("Este veículo foi marcado como seguro. Pontuação de notícias verdadeiras: " +
                             str(round(pontuacao['domain_score']['score_safe'], 2)))

            # Pontuação da Postagem
            if score_table['tc'] <= float(pontuacao['post']['truth_score']) < score_table['safe']:
                halo.warn("Esta notícia é segura mas possivelmente tendenciosa! E obteve pontuação " +
                          str(round(pontuacao['post']['truth_score'], 2)))
            elif float(pontuacao['post']['truth_score']) < score_table['tc']:
                halo.fail("Esta notícia foi marcada como falsa ou clickbait. E obteve pontuação " +
                          str(round(pontuacao['post']['truth_score'], 2)))
            else:
                halo.succeed("Esta notícia foi marcada como segura. E possui pontuação " +
                             str(round(pontuacao['post']['truth_score'], 2)))
        except Exception as e:
            halo.fail("Ocorreu um erro e não foi possível continuar (Erro: " + str(e) + ")")


def debug(url):
    print(extract(url)['article_title'])
    print(score(url, force_db=True))
