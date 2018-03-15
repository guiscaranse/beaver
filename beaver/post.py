from goose3 import Goose

settings = dict({'language': "pt_BR"})

def extract(url):
    g = Goose({'use_meta_language': False, 'target_language': settings['language']})
    response = dict()
    artigo = g.extract(url=url)
    response['article_title'] = artigo.title
    response['author'] = artigo.authors
    response['domain'] = artigo.domain
    response['date'] = artigo.publish_date
    response['text'] = artigo.cleaned_text
    return response
