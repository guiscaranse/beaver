import sys

import beaver

if len(sys.argv) == 1:
    # Verdade
    beaver.magiceye.magic("https://g1.globo.com/rj/rio-de-janeiro/noticia/policia-acredita-que-assassinos-da-vereadora"
                          "-marielle-seguiram-o-carro-em-que-ela-estava.ghtml")

    # Falsa
    beaver.magiceye.magic("https://www.sensacionalista.com.br/2018/03/14/temer-diz-que-seu-governo-pode-ser-o-melhor"
                          "-da-historia-do-brasil-e-deixa-humoristas-desempregados/")

    # Falsa
    beaver.magiceye.magic("http://www.socialistamorena.com.br/as-129-mulheres-que-morreram/")
else:
    beaver.magiceye.debug(sys.argv[1])
