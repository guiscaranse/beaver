import inspect
import os

import pandas
from sklearn import model_selection
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB

import beaver
from beaver import learning
from beaver.config import headers

model = ExtraTreesClassifier()
module_path = os.path.dirname(inspect.getfile(learning))


def train():
    """
    Divide os datasets e insere dentro do modelo definido, treina-o, e disponibiliza para consulta
    """
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    # Separar dados de validação, e dados de treino
    array = dataset.values
    # Dados
    X = array[:, 0:24]  # Dados
    Y = array[:, 24]  # Resultados
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


def describe():
    import matplotlib.pyplot as plt
    module_path = os.path.dirname(inspect.getfile(learning))
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    print("Sumary: \n" + str(dataset.shape))
    print("Head: \n" + str(dataset.head(20)))
    print("Describe:\n" + str(dataset.describe()))
    print(dataset.groupby('result').size())
    pandas.plotting.scatter_matrix(dataset)
    plt.show()


def check_models():
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
