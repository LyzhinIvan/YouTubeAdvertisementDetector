from AdDetectorModel.utils.scenes import SceneDetectionManager
from AdDetectorModel.utils.subtitles import Subtitles
from AdDetectorModel.utils.texts import preprocess_russian_text
import nltk


class AdDetectorModel:
    def __init__(self):
        pass

    def save(self, path):
        pass

    def load(self, path):
        pass

    def find_ads(self, video_ids):
        if not isinstance(video_ids, list):
            video_ids = [video_ids]
        result = []
        buzz_words = ['ссылка', 'ссылочка', 'переходить', 'описание', 'партнер', 'скидка', 'купон',
                      'распродажа', 'внизу', 'акция', 'рекомендуем', 'процент']
        sno = nltk.stem.SnowballStemmer('russian')
        buzz_words = list(map(sno.stem, buzz_words))

        for video_id in video_ids:
            subs = Subtitles(video_id, preprocess_russian_text)
            sdm = SceneDetectionManager()
            scenes = sdm.detect_scenes(video_id)
            scene_weights = []
            ads = []
            for scene in scenes:
                scene_subs = subs.fulltext(scene[0], scene[1])
                scene_weight = len(list(filter(lambda term: term in buzz_words, scene_subs.split())))
                if scene_weight > 3:
                    ads.append(scene)
                scene_weights.append(scene_weight)
            result.append(ads)

        return result if len(result) > 1 else result[0]

    def train(self, markups):
        pass
