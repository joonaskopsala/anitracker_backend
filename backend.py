import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

JIKAN_API_URL = 'https://api.jikan.moe/v4/seasons/now'

def fetch_all_airing_anime():
    all_anime = []
    page = 1
    while True:
        response = requests.get(f'{JIKAN_API_URL}?page={page}')
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                break
            all_anime.extend(data)
            page += 1
        else:
            break
    
    return all_anime

@app.route('/airing_anime', methods=['GET'])
def airing_anime():
    data = fetch_all_airing_anime()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
