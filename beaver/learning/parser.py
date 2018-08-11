import csv
import inspect
import os
import matplotlib.pyplot as plt
import numpy
import pandas

import beaver
from beaver import learning
from beaver.config import headers


def describe(gen_csv=False, gen_graphics=True):
    import beaver.learning
    module_path = os.path.dirname(inspect.getfile(beaver.learning))
    dataset = pandas.read_csv(module_path + "/data/dataset.csv", names=headers)
    print("Sumary: \n" + str(dataset.shape))
    print("Head: \n" + str(dataset.head(20)))
    print("Describe:\n" + str(dataset.describe()))
    print(dataset.groupby('result').size())
    print("Correlations:\n" + str(dataset.corr()))
    if gen_csv:
        dataset.describe().to_csv("describe.csv")
        dataset.corr().to_csv("corr.csv")
    if gen_graphics:
        pandas.plotting.scatter_matrix(dataset)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cax = ax.matshow(dataset.corr(), vmin=-1, vmax=1)
        fig.colorbar(cax)
        ticks = numpy.arange(0, len(headers), 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(headers, rotation='vertical')
        ax.set_yticklabels(headers)
        plt.show()


def build_data():
    """
    Constrói o dataset com base no levantamentos.csv
    """
    module_path = os.path.dirname(inspect.getfile(learning))
    with open(module_path + "/data/dataset.csv", 'w', newline='') as csvfile:
        with open(module_path + "/data/levantamentos.csv", 'r') as readfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, restval='0')
            reader = csv.DictReader(readfile)
            for row in reader:
                row_write = dict()
                data = beaver.analyse.score(row['URL'])
                for key in data['post'].keys():
                    if key in headers:
                        row_write[key] = data['post'][key]
                for key in data['polyglot']['grammar'].keys():
                    if key in headers:
                        if key is not "polarity":
                            row_write[key] = data['polyglot']['grammar'][key]
                if data['polyglot']['polarity'] is not 0:
                    if key in headers:
                        for key in data['polyglot']['polarity'].keys():
                            row_write[key] = data['polyglot']['polarity'][key]
                for key in data['other'].keys():
                    if key in headers:
                        row_write[key] = data['other'][key]
                if row['Supervisor'] == "Verdadeira":
                    row_write['result'] = 1
                else:
                    row_write['result'] = 0.0
                writer.writerow(row_write)
    lines = open(module_path + "/data/dataset.csv").readlines()
    # [random.shuffle(lines) for _ in range(50)]
    open(module_path + "/data/dataset.csv", 'w').writelines(lines)
