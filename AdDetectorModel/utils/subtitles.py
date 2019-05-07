import webvtt
from AdDetectorUtils.paths import get_subs_path


class Caption:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return '{}-{} -> {}'.format(self.start, self.end, self.text)

    def __repr__(self):
        return self.__str__()


class Subtitles:
    def __init__(self, video_id, text_filter=lambda t: t):
        self.captions = [Caption(cap.start_in_seconds, cap.end_in_seconds, text_filter(cap.text)) for cap in webvtt.read(get_subs_path(video_id)).captions]

    def __iter__(self):
        for caption in self.captions:
            yield caption

    def __getitem__(self, index):
        return self.captions[index]

    def fulltext(self, start=0, end=None):
        if not end:
            end = self.captions[-1].end
        subs = []
        for cap in self.captions:
            if start <= cap.start and cap.end <= end:
                subs.append(cap.text)
        return ' '.join(subs)
