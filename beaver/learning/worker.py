import inspect
import os

import pandas
from sklearn import model_selection
from sklearn.naive_bayes import GaussianNB

import beaver
from beaver.config import headers

model = GaussianNB()
module_path = os.path.dirname(inspect.getfile(beaver.learning))


def train():
    """
    Divide os datasets e insere dentro do modelo definido, treina-o, e disponibiliza para consulta
    """
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    # Separar dados de validação, e dados de treino
    array = dataset.values
    # Dados
    X = array[:, 0:26]  # Dados
    Y = array[:, 26]  # Resultados
    validation_size = 0.20  # Divide datasets
    global X_train, X_validation, Y_train, Y_validation
    X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y,
                                                                                    test_size=validation_size,
                                                                                    random_state=7)
    model.fit(X_train, Y_train)


def predict(url: str) -> list:
    """
    Prevê se uma notícia é verdadeira ou falsa (1 para verdadeiro, ou 0 para falsa)
    :param url: a URL a ser analisada
    :return: Retorna uma lista de probabilidade (1° coluna: chance de ser verdadeira, 2° coluna: chance de ser falsa)
    """
    train()
    info = dict()
    for head in headers:
        info[head] = 0
    info.pop('result', None)
    data = beaver.analyse.score(url)
    for key in data['post'].keys():
        info[key] = data['post'][key]
    for key in data['polyglot']['grammar'].keys():
        if key is not "polarity":
            info[key] = data['polyglot']['grammar'][key]
    if data['polyglot']['polarity'] is not 0:
        for key in data['polyglot']['polarity'].keys():
            info[key] = data['polyglot']['polarity'][key]
    planet = []
    universe = []
    for value in info.values():
        planet.append(value)
    universe.append(planet)
    return model.predict_proba(universe)
