import json

from flask import Flask

app = Flask(__name__)


@app.route('/<string:videoId>')
def get_ads(videoId):
    result = {'videoId': videoId, 'status': 'OK', 'ads': []}
    return json.dumps(result)


app.run(port=1234)
