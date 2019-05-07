import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")

sno = nltk.stem.SnowballStemmer('russian')
russian_stopwords = set(stopwords.words("russian"))
russian_alphabet = set('йцукенгшщзхъфывапролджэячсмитьбю')


def is_russian_word(word: str):
    return all(c in russian_alphabet for c in word.lower())


def preprocess_russian_text(text):
    tokens = map(str.strip, text.lower().split())
    tokens = filter(lambda token: is_russian_word(token), tokens)
    tokens = filter(lambda token: token not in russian_stopwords, tokens)
    tokens = map(sno.stem, tokens)
    return ' '.join(tokens)
