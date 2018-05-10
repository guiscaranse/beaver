import inspect
import os

import matplotlib.pyplot as plt
import pandas
from sklearn import model_selection
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from factory.settings import headers


def describe():
    import factory
    module_path = os.path.dirname(inspect.getfile(factory))
    dataset = pandas.read_csv(module_path + "/data/analyse.csv", names=headers)
    print("Sumary: \n" + str(dataset.shape))
    print("Head: \n" + str(dataset.head(20)))
    print("Describe:\n" + str(dataset.describe()))
    print(dataset.groupby('result').size())
    pandas.plotting.scatter_matrix(dataset)
    plt.show()


def prediction():
    import factory
    module_path = os.path.dirname(inspect.getfile(factory))
    dataset = pandas.read_csv(module_path + "/data/analyse.csv", names=headers)
    # Separar dados de validação, e dados de treino
    array = dataset.values
    # Dados
    X = array[:, 0:25]  # Dados
    Y = array[:, 25]  # Resultados
    print(Y)
    validation_size = 0.20  # Divide datasets
    seed = 7  # Semente
    X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size,
                                                                                    random_state=seed)
    scoring = 'accuracy'
    models = [('LR', LogisticRegression()), ('LDA', LinearDiscriminantAnalysis()), ('KNN', KNeighborsClassifier()),
              ('CART', DecisionTreeClassifier()), ('NB', GaussianNB()), ('SVM', SVC())]
    # evaluate each model in turn
    results = []
    names = []
    for name, model in models:
        kfold = model_selection.KFold(n_splits=10, random_state=seed)
        cv_results = model_selection.cross_val_score(model, X_train, Y_train, cv=kfold, scoring=scoring)
        results.append(cv_results)
        names.append(name)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)
