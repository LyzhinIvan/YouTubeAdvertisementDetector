import os

import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from keras.layers import Dense, LSTM, TimeDistributed, Bidirectional
from keras.models import Sequential, model_from_json

from AdDetectorModel.models import BaseAdDetectorModel
from AdDetectorModel.utils.scenes import SceneDetectionManager
from AdDetectorModel.utils.subtitles import Subtitles
from AdDetectorModel.utils.texts import preprocess_russian_text_with_morph
from AdDetectorModel.utils.youtube import VideoInfo


class D2VLSTMBasedModel(BaseAdDetectorModel):
    def __init__(self):
        super().__init__()
        self.sdm = SceneDetectionManager(detector_type='content', threshold=20, save_scenes=True)
        self.vectorizer = None
        self.subs_part_len = 10
        self.subs_classifier = None
        self._fitted = False
        self.window = 3

    def save(self, path):
        if not self._fitted:
            raise Exception("Model is not fitted yet. Fit model before saving.")
        if os.path.exists(path) and not os.path.isdir(path):
            raise Exception("Path for saving should be directory.")
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, 'lstm.json'), "w") as f:
            f.write(self.subs_classifier.to_json())
        self.subs_classifier.save_weights(os.path.join(path, 'lstm.weights'))

    def load(self, path):
        with open(os.path.join(path, 'lstm.json'), "w") as f:
            self.subs_classifier = model_from_json(f.read())
        self.subs_classifier.load_weights(os.path.join(path, 'lstm.weights'))
        self._fitted = True

    def find_ads(self, video_ids):
        if not isinstance(video_ids, list):
            video_ids = [video_ids]
        result = []

        for video_id in video_ids:
            info = VideoInfo(video_id)
            subs = Subtitles(video_id, preprocess_russian_text_with_morph)
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            xs = []
            segments = []
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                words = list(map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split()))
                x = list(self.vectorizer.infer_vector(words))
                x.append((scenes[l][0] + scenes[r][1]) / 2 / info.duration)
                xs.append(x)
                segments.append((scenes[l][0], scenes[r][1]))

            segments = [(0, 0)] * (self.window // 2) + segments + [(0, 0)] * (self.window // 2)
            features = len(xs[0])
            xs = [[0] * features] * (self.window // 2) + xs + [[0] * features] * (self.window // 2)
            X = []
            for i in range(self.window // 2, len(xs) - self.window // 2):
                X.append(xs[i - self.window // 2: i + self.window // 2 + 1])
            X = np.array(X)
            Y = self.subs_classifier.predict(X) > 0.5
            ads = []
            for i in range(self.window // 2, len(X) - self.window // 2):
                cnt = 0
                for d in range(-(self.window // 2), self.window // 2 + 1):
                    cnt += Y[i + d][self.window // 2 - d][0]
                if cnt > self.window // 2:
                    ads.append(segments[i])

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
        print('start model training')
        tagged_data = []
        subs_parts = []
        Ys = []
        ps = []
        for idx, video_id in enumerate(video_ids):
            print('\rprocessing video {} ({}/{})'.format(video_id, idx + 1, len(video_ids)), end='')
            subs = Subtitles(video_id, preprocess_russian_text_with_morph)
            scenes = self.sdm.detect_scenes(video_id)
            r = 0
            sp = []
            ys = []
            p = []
            info = VideoInfo(video_id)
            for l in range(len(scenes)):
                while r + 1 < len(scenes) and scenes[r][1] - scenes[l][0] < self.subs_part_len:
                    r += 1
                seg = (scenes[l][0], scenes[r][1])
                words = list(map(str.strip, subs.fulltext(scenes[l][0], scenes[r][1]).split()))
                sp.append(words)
                tagged_data.append(TaggedDocument(words=words, tags=[str(len(tagged_data))]))
                p.append((seg[0] + seg[1]) / 2 / info.duration)
                if self._inside_ad(seg, markups[video_id]):
                    ys.append(1)
                elif self._intersect_ad(seg, markups[video_id]):
                    ys.append(0.5)
                else:
                    ys.append(0)
            subs_parts.append(sp)
            Ys.append(ys)
            ps.append(p)
        self.vectorizer = Doc2Vec(size=50, alpha=0.025, dm=0)
        self.vectorizer.build_vocab(tagged_data)
        self.vectorizer.train(tagged_data, total_examples=self.vectorizer.corpus_count, epochs=500)
        X = []
        Y = []
        for idx, video_id in enumerate(video_ids):
            print('\rprocessing video {} ({}/{})'.format(video_id, idx + 1, len(video_ids)), end='')
            xs = [self.vectorizer.infer_vector(words) for words in subs_parts[idx]]
            xs = list(np.hstack((xs, np.reshape(ps[idx], (len(ps[idx]), 1)))).tolist())
            ys = Ys[idx]
            features = len(xs[0])
            xs = [[0] * features] * (self.window // 2) + xs + [[0] * features] * (self.window // 2)
            ys = [0] * (self.window // 2) + ys + [0] * (self.window // 2)
            for i in range(self.window // 2, len(xs) - self.window // 2):
                X.append(xs[i - self.window // 2: i + self.window // 2 + 1])
                Y.append(ys[i - self.window // 2: i + self.window // 2 + 1])

        X = np.array(X)
        Y = np.array(Y)
        Y = Y.reshape((Y.shape[0], Y.shape[1], 1))
        print(X.shape, Y.shape)
        model = Sequential()
        model.add(Bidirectional(LSTM(100, return_sequences=True), input_shape=(self.window, X.shape[2])))
        model.add(TimeDistributed(Dense(1, activation='sigmoid')))
        model.compile(optimizer='adam', loss='binary_crossentropy')
        np.random.seed(0)
        model.fit(X, Y, batch_size=len(X), shuffle=True, epochs=500)
        self.subs_classifier = model
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