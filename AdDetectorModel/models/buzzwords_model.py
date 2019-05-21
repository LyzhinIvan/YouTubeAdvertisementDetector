from AdDetectorModel.models import BaseAdDetectorModel
from AdDetectorModel.utils.scenes import SceneDetectionManager
from AdDetectorModel.utils.subtitles import Subtitles
from AdDetectorModel.utils.texts import preprocess_russian_text
from AdDetectorModel.utils.youtube import VideoInfo
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier

class BuzzwordsBasedModel(BaseAdDetectorModel):
    def __init__(self):
        super().__init__()
        self.stemmer = nltk.stem.SnowballStemmer('russian')
        self.sdm = SceneDetectionManager(detector_type='content', threshold=20, save_scenes=True)
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
            info = VideoInfo(video_id)
            subs = Subtitles(video_id, preprocess_russian_text)
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            ads = []
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                words = map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split())
                words = filter(lambda word: word in self.buzz_words, words)
                words = map(lambda word: self.buzz_words[word], words)
                subs_part = ' '.join(words)
                x = list(self.vectorizer.transform([subs_part]).toarray()[0])
                x.append(scenes[l][0] / info.duration)
                y = self.subs_classifier.predict([x])[0]
                if y == 1:
                    ads.append((scenes[l][0], scenes[r][1]))
            merged_ads = []
            for ad in ads:
                if len(merged_ads) == 0 or ad[0] - merged_ads[-1][1] > 10:
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
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                words = map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split())
                words = filter(lambda word: word in self.buzz_words, words)
                words = map(lambda word: self.buzz_words[word], words)
                subs_part = ' '.join(words)
                x = list(self.vectorizer.transform([subs_part]).toarray()[0])
                info = VideoInfo(video_id)
                x.append(scenes[l][0] / info.duration)
                seg = (scenes[l][0], scenes[r][1])
                if self._intersect_ad(seg, markups[video_id]):
                    continue
                X.append(x)
                if self._inside_ad(seg, markups[video_id]):
                    Y.append(1)
                else:
                    Y.append(0)
        print('X size: ', len(X))
        self.subs_classifier = CatBoostClassifier(iterations=150, max_depth=3, random_state=0)
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