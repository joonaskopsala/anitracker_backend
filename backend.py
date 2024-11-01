import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

load_dotenv()

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
app.config["JWT_EXPIRATION_DELTA"] = timedelta(hours=1)

mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client["anitracker"]
users_collection = db["users"]

JIKAN_API_URL = 'https://api.jikan.moe/v4/'

def verify_token(token):
    try:
        decoded_token = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def fetch_all_airing_anime():
    all_anime = []
    page = 1
    while True:
        response = requests.get(f'{JIKAN_API_URL}seasons/now?page={page}')
        if response.status_code == 200:
            data = response.json().get('data', [])
            if not data:
                break
            all_anime.extend(data)
            page += 1
        else:
            break
    return all_anime

def fetch_all_seasons():
    seasons = []
    response = requests.get(f'{JIKAN_API_URL}seasons/')
    if response.status_code == 200:
        seasons = response.json().get('data', [])
    else:
        return "Error"
    return seasons

@app.route('/airing_anime', methods=['GET'])
def airing_anime():
    data = fetch_all_airing_anime()
    return jsonify(data)

@app.route('/seasons', methods=['GET'])
def seasons():
    data = fetch_all_seasons()
    return jsonify(data)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.check_password_hash(user["password"], password):
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = {"username": username, "password": hashed_password}
    users_collection.insert_one(user)

    return jsonify({"msg": "User registered successfully"}), 201

@app.route("/profile", methods=["GET"])
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or malformed"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = verify_token(token)
    
    if not decoded_token:
        return jsonify({"error": "Invalid or expired token"}), 401

    username = decoded_token.get("username")
    
    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {
        "username": user["username"],
        "email": user.get("email", ""),
        "profilePicture": user.get("profilePicture", "")
    }
    
    return jsonify(user_data), 200

if __name__ == '__main__':
    app.run(debug=True)
