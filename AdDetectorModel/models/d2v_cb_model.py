import os

from catboost import CatBoostClassifier
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from imblearn.over_sampling import RandomOverSampler
import numpy as np

from AdDetectorModel.models import BaseAdDetectorModel
from AdDetectorModel.utils.scenes import SceneDetectionManager
from AdDetectorModel.utils.subtitles import Subtitles
from AdDetectorModel.utils.texts import preprocess_russian_text_with_morph
from AdDetectorModel.utils.youtube import VideoInfo

class D2VBasedModel(BaseAdDetectorModel):
    def __init__(self):
        super().__init__()
        self.sdm = SceneDetectionManager(detector_type='content', threshold=20, save_scenes=True)
        self.vectorizer = None
        self.subs_part_len = 10
        self.subs_classifier = None
        self._fitted = False

    def save(self, path):
        if not self._fitted:
            raise Exception("Model is not fitted yet. Fit model before saving.")
        if os.path.exists(path) and not os.path.isdir(path):
            raise Exception("Path for saving should be directory.")
        if not os.path.exists(path):
            os.mkdir(path)
        self.subs_classifier.save_model(os.path.join(path, 'catboost.model'))

    def load(self, path):
        self.subs_classifier = CatBoostClassifier()
        self.subs_classifier.load_model(os.path.join(path, 'catboost.model'))
        self._fitted = True

    def find_ads(self, video_ids):
        if not self._fitted:
            raise Exception("Train or load model before inference")

        if not isinstance(video_ids, list):
            video_ids = [video_ids]
        result = []

        for video_id in video_ids:
            info = VideoInfo(video_id)
            subs = Subtitles(video_id, preprocess_russian_text_with_morph)
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            ads = []
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                words = list(map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split()))
                x = self.vectorizer.infer_vector(words)
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
        Y = []
        print('start model training')
        tagged_data = []
        subs_parts = []
        for idx, video_id in enumerate(video_ids):
            print('\rprocessing video {} ({}/{})'.format(video_id, idx + 1, len(video_ids)), end='')
            subs = Subtitles(video_id, preprocess_russian_text_with_morph)
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                seg = (scenes[l][0], scenes[r][1])
                if self._intersect_ad(seg, markups[video_id]):
                    continue
                words = list(map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split()))
                subs_parts.append(words)
                tagged_data.append(TaggedDocument(words=words, tags=[str(len(tagged_data))]))
                if self._inside_ad(seg, markups[video_id]):
                    Y.append(1)
                else:
                    Y.append(0)
        self.vectorizer = Doc2Vec(size=50, alpha=0.025, dm=0)
        self.vectorizer.build_vocab(tagged_data)
        self.vectorizer.train(tagged_data, total_examples=self.vectorizer.corpus_count, epochs=500)
        X = np.array([self.vectorizer.infer_vector(words) for words in subs_parts])
        Y = np.array(Y)
        print('X shape: ', X.shape)
        print('Y shape: ', Y.shape)
        X, Y = RandomOverSampler(random_state=0, ratio=0.1).fit_resample(X, Y)
        self.subs_classifier = CatBoostClassifier(iterations=150, random_state=0)
        self.subs_classifier.fit(X, Y)
        self._fitted = True

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