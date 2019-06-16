from flask import Flask, jsonify
from flask_cors import CORS
from pika import BlockingConnection, ConnectionParameters
from pymongo import MongoClient

from AdDetectorUtils.config import config

app = Flask(__name__)
CORS(app)

print('Connecting to RabbitMQ...', end='')
queue_conn = BlockingConnection(ConnectionParameters(
    host=config.get('rabbitmq', 'Host') or 'localhost',
    port=config.get('rabbitmq', 'Port') or 5672))
channel = queue_conn.channel()
channel.queue_declare("queries")
print('OK')

print('Connecting to MongoDB...', end='')
mongo_host = config.get('mongo', 'Host') or 'localhost'
mongo_port = int(config.get('mongo', 'Port')) or 27017
mongo_db_name = config.get('mongo', 'Database') or 'addetector'
mongo_query_results = MongoClient(mongo_host, mongo_port)\
    .get_database(mongo_db_name)\
    .get_collection('query_results')
print('OK')


@app.route('/<video_id>')
def get_ads(video_id):
    obj = mongo_query_results.find_one({'videoId': video_id})
    if obj is None:
        obj = {'videoId': video_id, 'status': 'IN_QUEUE'}
        mongo_query_results.insert_one(obj)
        channel.basic_publish(exchange='',
                              routing_key='queries',
                              body=video_id)
        result = {'videoId': video_id, 'status': 'IN_QUEUE'}
    else:
        result = {'videoId': video_id, 'status': obj['status']}
        if 'ads' in obj:
            result['ads'] = obj['ads']
    print(result)
    return jsonify(result)


app.run(port=1234)
