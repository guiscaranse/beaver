import csv
import inspect
import os

import beaver
from beaver import learning
from beaver.config import headers


def build_data():
    module_path = os.path.dirname(inspect.getfile(learning))
    with open(module_path + "/data/dataset.csv", 'w', newline='') as csvfile:
        with open(module_path + "/data/levantamentos.csv", 'r') as readfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, restval='0')
            reader = csv.DictReader(readfile)
            for row in reader:
                row_write = dict()
                data = beaver.analyse.score(row['URL'])
                for key in data['post'].keys():
                    row_write[key] = data['post'][key]
                for key in data['polyglot']['grammar'].keys():
                    if key is not "polarity":
                        row_write[key] = data['polyglot']['grammar'][key]
                if data['polyglot']['polarity'] is not 0:
                    for key in data['polyglot']['polarity'].keys():
                        row_write[key] = data['polyglot']['polarity'][key]
                if row['Supervisor'] == "Verdadeira":
                    row_write['result'] = 1
                else:
                    row_write['result'] = 0.0
                writer.writerow(row_write)
    lines = open(module_path + "/data/dataset.csv").readlines()
    # [random.shuffle(lines) for _ in range(50)]
    open(module_path + "/data/dataset.csv", 'w').writelines(lines)
