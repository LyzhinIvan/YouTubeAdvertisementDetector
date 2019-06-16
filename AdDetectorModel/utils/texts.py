import nltk
from nltk.corpus import stopwords
import pymorphy2 as pm

nltk.download("stopwords")

ru_stemmer = nltk.stem.SnowballStemmer('russian')
en_stemmer = nltk.stem.PorterStemmer()
russian_stopwords = set(stopwords.words("russian"))
english_stopwords = set(stopwords.words("english"))
russian_alphabet = set('йцукенгшщзхъфывапролджэячсмитьбю')
english_alphabet = set('qwertyuiopasdfghjklzxcvbnm')
morph = pm.MorphAnalyzer()

def is_russian_word(word: str):
    return all(c in russian_alphabet for c in word.lower())


def is_english_word(word: str):
    return all(c in english_alphabet for c in word.lower())


def tokenize(text):
    return map(str.strip, text.lower().split())


def preprocess_russian_text(text):
    tokens = tokenize(text)
    tokens = filter(lambda token: is_russian_word(token), tokens)
    tokens = filter(lambda token: token not in russian_stopwords, tokens)
    tokens = map(ru_stemmer.stem, tokens)
    return ' '.join(tokens)


def preprocess_russian_text_with_morph(text):
    tokens = tokenize(text)
    tokens = filter(lambda token: is_russian_word(token), tokens)
    tokens = filter(lambda token: token not in russian_stopwords, tokens)
    tokens = map(lemmatize, tokens)
    return ' '.join(tokens)


def preprocess_english_text(text):
    tokens = tokenize(text)
    tokens = filter(lambda token: is_english_word(token), tokens)
    tokens = filter(lambda token: token not in english_stopwords, tokens)
    tokens = map(en_stemmer.stem, tokens)
    return ' '.join(tokens)


def lemmatize(word):
    return morph.parse(word)[0].normal_form
