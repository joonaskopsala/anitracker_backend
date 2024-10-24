from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

ANILIST_API_URL = 'https://graphql.anilist.co'

def fetch_airing_anime():
    query = '''
    query {
      Page {
        airingSchedules {
          media {
            title {
              english
              native
            }
            coverImage {
              large
            }
          }
          episode
          airingAt
        }
      }
    }
    '''
    response = requests.post(ANILIST_API_URL, json={'query': query})
    return response.json()

@app.route('/airing_anime', methods=['GET'])
def airing_anime():
    data = fetch_airing_anime()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
