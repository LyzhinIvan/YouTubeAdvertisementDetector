from AdDetectorModel.utils.scenes import SceneDetectionManager
from AdDetectorModel.utils.subtitles import Subtitles
from AdDetectorModel.utils.texts import preprocess_russian_text
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier


class AdDetectorModel:
    def __init__(self):
        self.stemmer = nltk.stem.SnowballStemmer('russian')
        self.sdm = SceneDetectionManager()
        self.buzz_words = {}
        with open('artifacts/buzzwords.txt', encoding='utf-8') as f:
            for line in f.readlines():
                words = list(map(str.strip, line.split()))
                if not words:
                    continue
                common_stem = self.stemmer.stem(words[0])
                for word in words:
                    self.buzz_words[self.stemmer.stem(word)] = common_stem
        self.vectorizer = CountVectorizer()
        self.vectorizer.vocabulary = set(self.buzz_words.values())
        self.subs_part_len = 10
        self.subs_classifier = None

    def save(self, path):
        pass

    def load(self, path):
        pass

    def find_ads(self, video_ids):
        if not isinstance(video_ids, list):
            video_ids = [video_ids]
        result = []

        for video_id in video_ids:
            subs = Subtitles(video_id, preprocess_russian_text)
            r = 0
            ads = []
            for l in range(len(subs.captions)):
                while r + 1 < len(subs.captions) and subs.captions[r].end - subs.captions[l].start < self.subs_part_len:
                    r += 1
                texts = map(lambda cap: cap.text, subs.captions[l:r + 1])
                texts = map(str.split, texts)
                texts = [filter(lambda word: word in self.buzz_words, text) for text in texts]
                texts = [map(lambda word: self.buzz_words[word], text) for text in texts]
                texts = [' '.join(text) for text in texts]
                subs_part = ' '.join(texts)
                x = self.vectorizer.transform([subs_part]).toarray()[0]
                y = self.subs_classifier.predict(x)
                if y == 1:
                    ads.append((subs.captions[l].start, subs.captions[r].end))
            merged_ads = []
            for ad in ads:
                if len(merged_ads) == 0 or merged_ads[-1][1] < ad[0]:
                    merged_ads.append(ad)
                else:
                    merged_ads.append((merged_ads.pop()[0], ad[1]))
            result.append(merged_ads)

        return result if len(result) > 1 else result[0]

    def train(self, markups):
        video_ids = list(markups.keys())
        X = []
        Y = []
        print('start model training')
        for idx, video_id in enumerate(video_ids):
            print('processing video {} ({}/{})'.format(video_id, idx + 1, len(video_ids)))
            subs = Subtitles(video_id, preprocess_russian_text)
            r = 0
            for l in range(len(subs.captions)):
                while r + 1 < len(subs.captions) and subs.captions[r].end - subs.captions[l].start < self.subs_part_len:
                    r += 1
                texts = map(lambda cap: cap.text, subs.captions[l:r + 1])
                texts = map(str.split, texts)
                texts = [filter(lambda word: word in self.buzz_words, text) for text in texts]
                texts = [map(lambda word: self.buzz_words[word], text) for text in texts]
                texts = [' '.join(text) for text in texts]
                subs_part = ' '.join(texts)
                x = self.vectorizer.transform([subs_part]).toarray()[0]
                seg = (subs.captions[l].start, subs.captions[r].end)
                if self._intersect_ad(seg, markups[video_id]):
                    continue
                X.append(x)
                if self._inside_ad(seg, markups[video_id]):
                    Y.append(1)
                else:
                    Y.append(0)
        print('X size: ', len(X))
        self.subs_classifier = CatBoostClassifier(iterations=100)
        self.subs_classifier.fit(X, Y)

    @staticmethod
    def _inside_ad(seg, ads):
        for ad in ads:
            if ad[0] <= seg[0] and seg[1] <= ad[1]:
                return True
        return False

    @staticmethod
    def _intersect_ad(seg, ads):
        for ad in ads:
            if seg[0] < ad[0] < seg[1] or seg[0] < ad[1] < seg[1]:
                return True
        return False
