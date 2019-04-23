import json
import time

from redis import Redis

from AdDetectorModel.model import AdDetectorModel


def main():
    model = AdDetectorModel()
    r = Redis(host='35.210.120.162', port=6379, db=0, decode_responses=True, encoding='utf-8')
    while True:
        video_id = r.lpop('queue')
        if not video_id:
            time.sleep(1)
        else:
            print('Processing video {}'.format(video_id))
            r.set(video_id, json.dumps(model.find_ads(video_id)))
            print('Finished {}'.format(video_id))


if __name__ == "__main__":
    main()