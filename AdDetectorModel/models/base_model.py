class BaseAdDetectorModel:
    def __init__(self):
        pass

    def save(self, path):
        pass

    def load(self, path):
        pass

    def find_ads(self, video_ids):
        return [[] for _  in video_ids] if isinstance(video_ids, list) else []

    def train(self, markups):
        pass