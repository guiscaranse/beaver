# Beaver

*Extração e análise de artigos da internet*

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/guiscaranse/beaver/blob/master/LICENSE)

***
## Instalando

Depende de:
* [Python 3](https://www.python.org/downloads/) (3+)
* [Pipenv](https://github.com/pypa/pipenv) (11.8+)
* [ICU4C](http://site.icu-project.org/download) (61.1+)
* [PyICU](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyicu) (Pré-Compilado para o Python utilizado)
* [pycld2](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycld2) (Pré-Compilado para o Python utilizado)

Instale as dependências do pipenv e inicie o ambiente virtual:
```sh
pipenv install
pipenv shell
```

É possível que a instalação acima falhe e você deve instalar os Wheels do `PyICU` e `pycld2` e deve-se instala-los manualmente usando como exemplo:
```sh
pipenv install ./PyICU.whl
```

> É necessário definir a variável de ambiente `MS_BING_KEY` com uma chave de busca gerada nos [Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/)


É possível executar o arquivo de testes usando:
```sh
python run.py
```

É possível rodar testes personalizados utilizando o exemplo abaixo:
```sh
python run.py https://www.sensacionalista.com.br/2018/03/14/temer-diz-que-seu-governo-pode-ser-o-melhor-da-historia-do-brasil-e-deixa-humoristas-desempregados/
```