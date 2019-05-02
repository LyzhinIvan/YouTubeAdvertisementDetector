import os
import json
import youtube_dl
import ffmpeg

from AdDetectorUtils.paths import *


class YouTubeDownloader:
    def _get_info_path(self, video_id):
        return join(get_dir(video_id), video_id + '.info.json')

    def load_info(self, video_id):
        if not os.path.exists(self._get_info_path(video_id)):
            opts = {
                'skip_download': True,
                'outtmpl': join(get_dir(video_id), video_id),
                'writeinfojson': True
            }
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])
        with open(self._get_info_path(video_id), 'r') as f:
            return json.load(f)

    def load_video(self, video_id):
        if video_exists(video_id):
            return
        opts = {
            'format': '(mp4)[height<=360]',
            'outtmpl': get_video_path(video_id)
        }
        with youtube_dl.YoutubeDL(opts) as ytdl:
            ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])

    def extract_audio(self, video_id):
        if audio_exists(video_id):
            return
        self.load_video(video_id)
        ffmpeg\
            .input(get_video_path(video_id))\
            .output(get_audio_path(video_id), acodec='copy')\
            .run()

    def load_subtitles(self, video_id, langs=('ru',)):
        for lang in langs:
            if subs_exists(video_id, lang):
                continue
            opts = {
                'writeautomaticsub': True,
                'subtitleslangs': langs,
                'subtitlesformat': 'vtt',
                'nooverwrites': True,
                'skip_download': True,
                'outtmpl': join(get_dir(video_id), video_id + '.vtt')
            }
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])

    def load_all(self, video_id):
        self.load_subtitles(video_id)
        self.load_video(video_id)
        self.extract_audio(video_id)
