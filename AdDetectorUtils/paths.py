from os.path import exists, join
from AdDetectorUtils.config import config


def get_dir(video_id):
    return join(config.get('paths', 'YouTubeData'), video_id)


def get_video_path(video_id):
    return join(config.get('paths', 'YouTubeData'), video_id, video_id + '.mp4')


def get_audio_path(video_id):
    return join(config.get('paths', 'YouTubeData'), video_id, video_id + '.aac')


def get_subs_path(video_id, lang='ru'):
    return join(config.get('paths', 'YouTubeData'), video_id, video_id + '.' + lang + '.vtt')


def get_info_path(video_id):
    return join(config.get('paths', 'YouTubeData'), video_id, video_id + '.info.json')


def video_exists(video_id):
    return exists(get_video_path(video_id))


def audio_exists(video_id):
    return exists(get_audio_path(video_id))


def subs_exists(video_id, lang='ru'):
    return exists(get_subs_path(video_id, lang))
