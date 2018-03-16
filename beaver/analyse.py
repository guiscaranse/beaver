from collections import Counter
from beaver import post, bing_search, gnews_search


def score(url):
    postagem = post.extract(url)
    print("Buscando por: ", postagem['article_title'])
    bing_relatives = bing_search.search_relatives(postagem['article_title'])
    gnews_relatives = gnews_search.search_relatives(postagem['article_title'])
    all_text = ""
    for news in bing_relatives['relatives']:
        try:
            all_text += news['text']
        except Exception:
            print("Não foi possível adicionar", news['text'])
            pass
    for news in gnews_relatives['relatives']:
        try:
            all_text += news['text']
        except Exception:
            print("Não foi possível adicionar", news['text'])
            pass
    print(Counter(all_text.split()).most_common())
