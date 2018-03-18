# Beaver

*Extração e análise de artigos da internet*

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/guiscaranse/beaver/blob/master/LICENSE)

***
## Instalando

Depende de:
* [Python 3](https://www.python.org/downloads/) (3+)
* [Pipenv](https://github.com/pypa/pipenv) (11.8+)

Instale as dependências do pipenv e inicie o ambiente virtual:
```sh
pipenv install
pipenv shell
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