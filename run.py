import sys

import beaver

print(beaver.magiceye.magic(sys.argv[1]))
'''
if len(sys.argv) == 1:
    # Verdade
    teste1 = beaver.analyse.score("https://g1.globo.com/rj/rio-de-janeiro/noticia/policia-acredita-que-assassinos-da"
                                  "-vereadora-marielle-seguiram-o-carro-em-que-ela-estava.ghtml")
    print(teste1)

    # Falsa
    teste2 = beaver.analyse.score("https://www.sensacionalista.com.br/2018/03/14/temer-diz-que-seu-governo-pode-ser-o-"
                                  "melhor-da-historia-do-brasil-e-deixa-humoristas-desempregados/")
    print(teste2)

    # Falsa
    teste3 = beaver.analyse.score("http://www.socialistamorena.com.br/as-129-mulheres-que-morreram/")
    print(teste3)
else:
    print("Analisando: ", sys.argv[1])
    print(beaver.analyse.score(sys.argv[1]))
'''
