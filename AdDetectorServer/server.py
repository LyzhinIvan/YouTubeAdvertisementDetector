import json

from flask import Flask, jsonify
from flask_cors import CORS
from redis import Redis

app = Flask(__name__)
CORS(app)

r = Redis(host='35.210.120.162', port=6379, db=0, decode_responses=True, encoding='utf-8')


@app.route('/<string:videoId>')
def get_ads(videoId):
    res = r.get(videoId)
    if res == 'IN_QUEUE':
        result = {'videoId': videoId, 'status': 'IN_QUEUE'}
    elif res is None:
        result = {'videoId': videoId, 'status': 'IN_QUEUE'}
        r.set(videoId, 'IN_QUEUE')
        r.rpush('queue', videoId)
    else:
        result = {'videoId': videoId, 'status': 'OK', 'ads': json.loads(res)}

    return jsonify(result)


app.run(port=1234)
