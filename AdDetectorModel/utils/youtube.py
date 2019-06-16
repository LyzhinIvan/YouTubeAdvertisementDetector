import os
import json
import youtube_dl
import ffmpeg
from pycaption import DFXPReader, WebVTTWriter

from AdDetectorUtils.paths import *


class YouTubeDownloader:
    def load_info(self, video_id):
        if not os.path.exists(get_info_path(video_id)):
            print('Loading info for {}'.format(video_id))
            opts = {
                'skip_download': True,
                'outtmpl': join(get_dir(video_id), video_id),
                'writeinfojson': True
            }
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])
        with open(get_info_path(video_id), 'r') as f:
            return json.load(f)

    def load_video(self, video_id):
        if video_exists(video_id):
            return
        print('Loading video for {}'.format(video_id))
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
        print('Extracting audio for {}'.format(video_id))
        ffmpeg\
            .input(get_video_path(video_id))\
            .output(get_audio_path(video_id), acodec='copy')\
            .run()

    def load_subtitles(self, video_id, langs=('ru',)):
        for lang in langs:
            if subs_exists(video_id, lang):
                continue
            print('Loading {} subtitles for {}'.format(lang, video_id))
            opts = {
                'writeautomaticsub': True,
                'subtitleslangs': langs,
                'subtitlesformat': 'ttml',
                'nooverwrites': True,
                'skip_download': True,
                'outtmpl': join(get_dir(video_id), video_id + '.ttml')
            }
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])
            # WevVTT captions from youtube contains duplicate phrases with overlapping time segments
            # It is not comfortable, that's why subtitles firstly downloaded in ttml format
            # Then subtitles converted to webvtt
            subs_path_ttml = join(get_dir(video_id), video_id + '.' + lang + '.ttml')
            subs_path_vtt = join(get_dir(video_id), video_id + '.' + lang + '.vtt')
            if exists(subs_path_ttml):
                print('converting subtitles')
                with open(subs_path_ttml, encoding='utf-8') as f:
                    subs = DFXPReader().read(f.read())
                with open(subs_path_vtt, 'w', encoding='utf-8') as f:
                    f.write(WebVTTWriter().write(subs))

    def load_all(self, video_id):
        self.load_subtitles(video_id)
        self.load_video(video_id)
        self.extract_audio(video_id)


class VideoInfo:
    def __init__(self, video_id):
        if not exists(get_info_path(video_id)):
            ytdl = YouTubeDownloader()
            ytdl.load_info(video_id)
        with open(get_info_path(video_id)) as f:
            self.info = json.load(f)
        self.duration = self.info['duration']
        self.fps = 25
        for f in self.info['formats']:
            if f['format_note'] == '360p' and f['ext'] == 'mp4':
                self.fps = f['fps']
                break
