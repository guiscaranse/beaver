# Beaver

>Este repositório foi descontinuado, o novo repositório pode ser encontrado em [verifique.me](https://github.com/verifiqueme/)

*Extração e análise de artigos da internet*

[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/guiscaranse/beaver/blob/master/LICENSE)

***
## Instalando

Depende de:
* [Python 3](https://www.python.org/downloads/) (3+)
* [Pipenv](https://github.com/pypa/pipenv) (11.8+)
* [ICU4C](http://site.icu-project.org/download) (61.1+)

### Windows
* [PyICU](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyicu) (Pré-Compilado para o Python utilizado)
* [pycld2](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycld2) (Pré-Compilado para o Python utilizado)

É possível que a instalação acima falhe e você deve instalar os Wheels do `PyICU` e `pycld2` e deve-se instala-los manualmente usando como exemplo:
```sh
pipenv install ./PyICU.whl
```

### Instalando dependências
Instale as dependências do pipenv e inicie o ambiente virtual:
```sh
pipenv install
pipenv shell
```

> É necessário definir a variável de ambiente `MS_BING_KEY` com uma chave de busca gerada nos [Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/)
