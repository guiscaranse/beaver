from halo import Halo

from beaver.analyse import score
from beaver.config import score_table


def magic(url):
    with Halo(text='Analisando noticias... Isto pode levar um tempo', spinner='dots') as halo:
        try:
            pontuacao = score(url)
            halo.succeed("Terminado análise, computando pontuação...")
            if score_table['tc'] <= float(pontuacao['truth_score']) < score_table['safe']:
                halo.warn("Esta notícia foi marcada como tendenciosa ou clickbait! E obteve pontuação " +
                          str(round(pontuacao['truth_score'], 2)))
            elif float(pontuacao['truth_score']) < score_table['tc']:
                halo.fail("Esta notícia foi marcada como falsa ou antiga. E obteve pontuação " +
                          str(round(pontuacao['truth_score'], 2)))
            else:
                halo.succeed("Esta notícia foi marcada como segura. E possui pontuação " +
                             str(round(pontuacao['truth_score'], 2)))
        except Exception as e:
            halo.fail("Ocorreu um erro e não foi possível continuar (Erro: " + str(e) + ")")
