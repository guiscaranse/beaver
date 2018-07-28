import inspect
import os
import pickle
from pathlib import Path

import numpy
import pandas
from keras.backend import clear_session
from sklearn import model_selection
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB

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


def fixed_model(force: bool = False) -> object:
    """
    Responsável de retornar um modelo compatível do scikit-learn, para evitar overfitting um dump de modelo será
    utilizado (modeldump) caso exista, caso não exista será gerado.
    :param force: Se deve forçar a geração de um modeldump
    :return: Modelo do scikit-learn já treinado
    """
    model_path = module_path + "/data/modeldump.data"
    if Path(model_path).is_file() and force is False:
        return pickle.load(open(model_path, 'rb'))
    else:
        model = GradientBoostingClassifier()
        train()
        if Path(model_path).is_file():  # Remove se o modelo já existe (Force = true)
            os.remove(model_path)
        model.fit(X_train, Y_train)
        pickle.dump(model, open(model_path, 'wb'))
        return model


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
    planet = []
    universe = []
    for value in info.values():
        planet.append(value)
    universe.append(planet)
    return keras_model().predict_proba(numpy.array(universe))


def check_models():
    """
    Gera uma lista mostrando a taxa de acerto de todos os modelos compatíveis listados em "models"
    """
    train()
    scoring = 'accuracy'
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    models = [('LR', LogisticRegression()), ('KNN', KNeighborsClassifier()),
              ('CART', DecisionTreeClassifier()), ('NB', GaussianNB()), ('SVM', SVC()),
              ("ETC", ExtraTreesClassifier()), ("GBC", GradientBoostingClassifier())]
    # evaluate each model in turn
    results = []
    names = []
    for name, modelt in models:
        kfold = model_selection.KFold(n_splits=10, random_state=7)
        cv_results = model_selection.cross_val_score(modelt, X_train, Y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)


def keras_model(force=False, verbose=False):
    """
    Método para retornar um modelo iterativo do Keras. Se um modelo já existir, carregará os pesos e retornará um objeto
    de modelo iterativo. Caso não exista um modelo, um será gerado.
    :param force: se deve ou não forçar a geração de um modelo fresco
    :param verbose: quando o verbose estiver ligado durante a criação de um modelo, mostrará a precisão do mesmo
    :return: modelo iterativo do keras
    """
    import numpy
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
        numpy.random.seed(7)
        dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
        # Separar dados de validação, e dados de treino
        array = dataset.values
        # Dados
        X = array[:, 0:(len(headers) - 1)]  # Dados
        Y = array[:, (len(headers) - 1)]  # Resultados
        model = Sequential()
        model.add(Dense(60, input_dim=(len(headers) - 1), activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(6, activation='relu'))
        model.add(Dense(3, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(X, Y, epochs=150, batch_size=10, verbose=0)
        if verbose:
            scores = model.evaluate(X, Y)
            print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))
        model_json = model.to_json()
        with open(model_path, "w") as json_file:
            json_file.write(model_json)
        model.save_weights(weights_path)
        return model


def half_train():
    """
    Código de teste de metade do dataset, é necessário dividir o dataset.csv, sendo o segundo arquivo validate.csv.
    """
    acertos = 0
    linhas = 0
    import csv
    with open(module_path + "/data/validate.csv") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            linhas += 1
            universe = numpy.array([row[0:(len(row) - 1)]])
            x = universe
            y = row[(len(row) - 1)]
            previsao = round(keras_model().predict(x)[0][0], 0)
            if float(previsao) == float(y):
                print("Acertou")
                acertos += 1
    print("Analisados: " + str(linhas))
    print("Acertos:" + str(acertos))
