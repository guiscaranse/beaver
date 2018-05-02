import inspect
import os

import pandas as pd

import beaver
import factory

headers = ['bing', 'google', 'relatives_bing_text', 'relatives_google_text', 'popular_bing',
           'popular_google', 'average_score', 'ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'DET', 'INTJ', 'NOUN',
           'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X', 'polarity', 'result']


def build_data():
    module_path = os.path.dirname(inspect.getfile(factory))
    df = pd.read_csv(module_path + '/data/levantamentos.csv')
    for item in df.to_dict()['URL'].values():
        print(beaver.analyse.score(item))
