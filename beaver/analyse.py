import nltk
from nltk.corpus import stopwords

from beaver import post, bing_search, gnews_search
from beaver.config import settings


def alltext_score(all_text):
    try:
        nltk.data.find('corpora\stopwords')
    except LookupError:
        nltk.download('stopwords')
    p_stopwords = set(stopwords.words('portuguese'))
    fd = nltk.FreqDist(w.lower() for w in all_text.split() if w not in p_stopwords)
    max_words = settings['max_words_precision']
    if len(list(fd.keys())) >= settings['max_words_precision']:
        for x in range(0, settings['max_words_precision']):
            if "," in list(fd)[x]:
                break
            max_words = x
        return list(fd.keys())[:max_words]
    else:
        for y in range(0, len(list(fd.keys()))):
            if "," in list(fd)[y]:
                break
            max_words = y
        return list(fd.keys())[:max_words]


def score(url):
    final_score = dict()
    postagem = post.extract(url)
    bing_relatives = bing_search.search_relatives(postagem['article_title'])
    gnews_relatives = gnews_search.search_relatives(postagem['article_title'])
    final_score['bing'] = bing_relatives['score']
    final_score['google'] = gnews_relatives['score']
    all_text = ""
    for news in bing_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text'], "utf8"))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass
    for news in gnews_relatives['relatives']:
        try:
            all_text += post.fixcharset(str(news['text'], "utf8"))
        except Exception:  # Ignora textos que não puderam ser entendidos
            pass
    popular_words = ' '.join(alltext_score(all_text))
    if len(popular_words) > 0:
        popular_words_gnews_relatives = gnews_search.search_relatives(popular_words)['score']
        popular_words_bing_relatives = bing_search.search_relatives(popular_words)['score']
        final_score['popular_bing'] = popular_words_bing_relatives
        final_score['popular_google'] = popular_words_gnews_relatives
    else:
        final_score['popular_bing'] = 0
        final_score['popular_google'] = 0
    final_score['truth_score'] = sum(final_score.values()) / float(len(final_score))
    return final_score
