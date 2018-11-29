import inspect
import os
from pathlib import Path

import numpy
import pandas
from keras.backend import clear_session
from sklearn import model_selection

import beaver
from beaver import learning
from beaver.config import headers

module_path = os.path.dirname(inspect.getfile(learning))


def train():
    """
    Divide os datasets e insere dentro do modelo definido, treina-o, e disponibiliza para consulta
    """
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    # Separar dados de validação, e dados de treino
    array = dataset.values
    # Dados
    X = array[:, 0:(len(headers) - 1)]  # Dados
    Y = array[:, (len(headers) - 1)]  # Resultados
    validation_size = 0.20  # Divide datasets
    global X_train, Y_train
    X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y,
                                                                                    test_size=validation_size,
                                                                                    random_state=7)


def predict(url: str) -> list:
    """
    Prevê se uma notícia é verdadeira ou falsa (1 para verdadeiro, ou 0 para falsa)
    :param url: a URL a ser analisada
    :return: Retorna uma lista de probabilidade (1° coluna: chance de ser verdadeira, 2° coluna: chance de ser falsa)
    """
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
    for key in data['other'].keys():
        if key in headers:
            info[key] = data['other'][key]
    planet = []
    universe = []
    for value in info.values():
        planet.append(value)
    universe.append(planet)
    return keras_model().predict_proba(numpy.array(universe))


def evaluate(keras_model, X, Y):
    scores = keras_model.evaluate(X, Y)
    return "%s: %.2f%%" % (keras_model.metrics_names[1], scores[1] * 100)


def keras_model(force=False, verbose=False):
    """
    Método para retornar um modelo iterativo do Keras. Se um modelo já existir, carregará os pesos e retornará um objeto
    de modelo iterativo. Caso não exista um modelo, um será gerado.
    :param force: se deve ou não forçar a geração de um modelo fresco
    :param verbose: quando o verbose estiver ligado durante a criação de um modelo, mostrará a precisão do mesmo
    :return: modelo iterativo do keras
    """
    from keras import Sequential
    from keras.layers import Dense
    model_path = module_path + "/data/kerasdump.data"
    weights_path = module_path + "/data/kerasweights.h5"
    if Path(model_path).is_file() and force is False:
        from keras.models import model_from_json
        clear_session()
        loaded_model = model_from_json(open(model_path, 'r').read())
        loaded_model.load_weights(weights_path)
        loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return loaded_model
    else:
        clear_session()
        dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
        # Separar dados de validação, e dados de treino
        array = dataset.values
        # Dados
        X = array[:, 0:(len(headers) - 1)]  # Dados
        Y = array[:, (len(headers) - 1)]  # Resultados
        numpy.random.seed(491826658)
        model = Sequential()
        model.add(Dense(52, input_dim=(len(headers) - 1), activation='relu'))
        model.add(Dense(29, activation='relu'))
        model.add(Dense(17, activation='relu'))
        model.add(Dense(5, activation='relu'))
        model.add(Dense(2, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X, Y, epochs=150, batch_size=10, verbose=0, shuffle=True)
        if verbose:
            print(evaluate(model, X, Y))
        model_json = model.to_json()
        with open(model_path, "w") as json_file:
            json_file.write(model_json)
        model.save_weights(weights_path)
        return model
