import json
import time

from redis import Redis

from AdDetectorModel.models import BuzzwordsBasedModel
from AdDetectorModel.utils.youtube import YouTubeDownloader


def main():
    model = BuzzwordsBasedModel()
    r = Redis(host='35.210.120.162', port=6379, db=0, decode_responses=True, encoding='utf-8')
    ytdl = YouTubeDownloader()
    while True:
        video_id = r.lpop('queue')
        if not video_id:
            time.sleep(1)
        else:
            print('Processing video {}'.format(video_id))
            info = ytdl.load_info(video_id)
            if info["is_live"]:
                r.set(video_id, "LIVE")
            else:
                ytdl.load_all(video_id)
                ads = model.find_ads(video_id)
                r.set(video_id, json.dumps(ads))
            print('Finished {}'.format(video_id))


if __name__ == "__main__":
    main()