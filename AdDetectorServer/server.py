from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/<string:videoId>')
def get_ads(videoId):
    result = {'videoId': videoId, 'status': 'OK', 'ads': []}
    return jsonify(result)


app.run(port=1234)
