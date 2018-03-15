import beaver

print("Testando primeiro...")
teste1 = beaver.post.extract("https://g1.globo.com/rj/rio-de-janeiro/noticia/policia-acredita-que-assassinos-da"
                             "-vereadora-marielle-seguiram-o-carro-em-que-ela-estava.ghtml")

print("Testando segundo...")
teste2 = beaver.post.extract("https://www.sensacionalista.com.br/2018/03/14/temer-diz-que-seu-governo-pode-ser-"
                             "o-melhor-da-historia-do-brasil-e-deixa-humoristas-desempregados/")

print(beaver.post.search_relatives(teste2['article_title']))
