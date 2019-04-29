import os
import youtube_dl
import ffmpeg


class YouTubeDownloader:
    def __init__(self, save_path='youtube-data'):
        self.save_path = save_path

    def _get_file_path(self, video_id):
        return self.save_path + '/{0}/{0}'.format(video_id)

    def _get_video_path(self, video_id):
        return self._get_file_path(video_id) + '.mp4'

    def _get_audio_path(self, video_id):
        return self._get_file_path(video_id) + '.aac'

    def _get_sub_path(self, video_id, lang='ru', format='vtt'):
        return '{}.{}'.format(self._get_file_path(video_id), lang, format)

    def load_video(self, video_id):
        if os.path.exists(self._get_video_path(video_id)):
            return
        opts = {
            'format': '(mp4)[height<=360]',
            'outtmpl': self._get_video_path(video_id)
        }
        with youtube_dl.YoutubeDL(opts) as ytdl:
            ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])

    def extract_audio(self, video_id):
        if os.path.exists(self._get_audio_path(video_id)):
            return
        self.load_video(video_id)
        ffmpeg\
            .input(self._get_video_path(video_id))\
            .output(self._get_audio_path(video_id), acodec='copy')\
            .run()

    def load_subtitles(self, video_id, langs=('ru',)):
        for lang in langs:
            if os.path.exists(self._get_sub_path(video_id, lang=lang)):
                continue
            opts = {
                'writeautomaticsub': True,
                'subtitleslangs': langs,
                'subtitlesformat': 'vtt',
                'nooverwrites': True,
                'skip_download': True,
                'outtmpl': self._get_file_path(video_id) + '.vtt'
            }
            with youtube_dl.YoutubeDL(opts) as ytdl:
                ytdl.download(['https://www.youtube.com/watch?v={}'.format(video_id)])

    def load_all(self, video_id):
        self.load_subtitles(video_id)
        self.load_video(video_id)
        self.extract_audio(video_id)
