import pendulum
from beaver.gtrends import interest_score
keywords = ["vereadora Marielle"]
timezone = pendulum.now('America/Sao_Paulo')
print(interest_score(keywords, timezone))