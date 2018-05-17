import inspect
import os

import matplotlib.pyplot as plt
import pandas
from sklearn import model_selection
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import beaver
from beaver.config import headers

model = GaussianNB()


def describe():
    from beaver import learning
    module_path = os.path.dirname(inspect.getfile(learning))
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    print("Sumary: \n" + str(dataset.shape))
    print("Head: \n" + str(dataset.head(20)))
    print("Describe:\n" + str(dataset.describe()))
    print(dataset.groupby('result').size())
    pandas.plotting.scatter_matrix(dataset)
    plt.show()


def train():
    from beaver import learning
    module_path = os.path.dirname(inspect.getfile(learning))
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    # Separar dados de validação, e dados de treino
    array = dataset.values
    # Dados
    X = array[:, 0:26]  # Dados
    Y = array[:, 26]  # Resultados
    validation_size = 0.20  # Divide datasets
    seed = 7  # Semente
    global X_train, X_validation, Y_train, Y_validation
    X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y,
                                                                                    test_size=validation_size,
                                                                                    random_state=seed)

    scoring = 'accuracy'
    models = [('LR', LogisticRegression()), ('LDA', LinearDiscriminantAnalysis()), ('KNN', KNeighborsClassifier()),
              ('CART', DecisionTreeClassifier()), ('NB', GaussianNB()), ('SVM', SVC()),
              ("ETC", ExtraTreesClassifier()), ("GBC", GradientBoostingClassifier())]
    # evaluate each model in turn
    results = []
    names = []
    for name, model in models:
        kfold = model_selection.KFold(n_splits=15, random_state=seed)
        cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        # msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())


def predict(data):
    model.fit(X_train, Y_train)
    predictions = model.predict(data)
    print(predictions)
    print("% verdadeira: ", round(float(model.predict_proba(data)[:, 1]), 2))
    print("% falsa: ", round(float(model.predict_proba(data)[:, 0]), 2))


def auto_predict(url):
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
    print(universe)
    predict(universe)
