from argparse import ArgumentParser

from pika import BlockingConnection, ConnectionParameters
from pymongo import MongoClient

from AdDetectorModel.models import BuzzwordsBasedModel
from AdDetectorModel.utils.youtube import YouTubeDownloader
from AdDetectorUtils.config import config
from AdDetectorUtils.paths import subs_exists, video_exists


print('Connecting to MongoDB...', end='')
mongo_host = config.get('mongo', 'Host') or 'localhost'
mongo_port = int(config.get('mongo', 'Port')) or 27017
mongo_db_name = config.get('mongo', 'Database') or 'addetector'
mongo_query_results = MongoClient(mongo_host, mongo_port)\
    .get_database(mongo_db_name)\
    .get_collection('query_results')
print('OK')


model = BuzzwordsBasedModel()

def process_query(ch, method, properties, video_id):
    video_id = video_id.decode(encoding='utf-8')
    print('Processing video {}'.format(video_id))

    ytdl = YouTubeDownloader()
    info = ytdl.load_info(video_id)
    result = {'videoId': video_id}
    if info['is_live']:
        result['status'] = 'LIVE'
    else:
        ytdl.load_subtitles(video_id)
        if not subs_exists(video_id):
            result['status'] = 'NO_SUBS'
        else:
            ytdl.load_video(video_id)
            if not video_exists(video_id):
                result['status'] = 'NO_VIDEO'
            else:
                ads = model.find_ads(video_id)
                result['status'] = 'OK'
                result['ads'] = ads
    print(result)
    mongo_query_results.update_one({'videoId': video_id}, {'$set': result})
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('Finished {}'.format(video_id))


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('--model-path', type=str)
    args = arg_parser.parse_args()

    print('Loading model...', end='')
    #model.load(args.model_path)
    print('OK')

    print('Connecting to RabbitMQ...', end='')
    queue_conn = BlockingConnection(ConnectionParameters(
        host=config.get('rabbitmq', 'Host') or 'localhost',
        port=config.get('rabbitmq', 'Port') or 5672))
    channel = queue_conn.channel()
    channel.queue_declare("queries")
    channel.basic_consume(queue='queries', on_message_callback=process_query)
    print('OK')
    channel.start_consuming()


if __name__ == "__main__":
    main()