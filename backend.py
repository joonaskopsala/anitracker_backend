import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

JIKAN_API_URL = 'https://api.jikan.moe/v4/seasons/now'

def fetch_airing_anime():
    response = requests.get(JIKAN_API_URL)
    if response.status_code == 200:
        data = response.json()
        airing_anime = []
        
        for anime in data['data']:
            airing_anime.append({
                'title': anime['title'],
                'episode': anime.get('episodes', 'Unknown'),
                'airing_start': anime['aired']['from'],
                'cover_image': anime['images']['jpg']['large_image_url']
            })
        
        return airing_anime
    else:
        return {'error': 'Failed to fetch data from Jikan API'}, response.status_code

@app.route('/airing_anime', methods=['GET'])
def airing_anime():
    data = fetch_airing_anime()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
