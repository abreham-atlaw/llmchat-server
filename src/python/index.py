from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import json_util
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb+srv://abrehamatlaw:7nQdrVrc5Jopp18F@cluster0.trf60oq.mongodb.net/?retryWrites=true&w=majority')
db = client['llmchat']
collection = db['requests']

@app.route('/api/request/new', methods=['POST'])
def create_request():
    data = request.get_json()
    query = data['query']
    now = datetime.now()

    request_data = {
        'query': query,
        'id': str(collection.count_documents({}) + 1),  # Generate unique ID
        'response': None,
        'lock_datetime': None,
        'response_datetime': None,
        'create_datetime': now
    }

    collection.insert_one(request_data)

    return jsonify({'request_id': request_data['id']})


@app.route('/api/request/get', methods=['GET'])
def get_request():
    request_data = collection.find_one({'lock_datetime': None, 'response_datetime': None})

    if request_data:
        request_id = request_data['id']
        now = datetime.now()
        collection.update_one({'id': request_id}, {'$set': {'lock_datetime': now}})
        request_data.pop("_id")
        return jsonify(request_data)
    else:
        return jsonify({'message': 'No available requests'}), 404


@app.route('/api/request/respond', methods=['POST'])
def respond_request():
    data = request.get_json()
    request_id = data['id']
    response = data['response']
    now = datetime.now()

    collection.update_one({'id': request_id}, {'$set': {'response': response, 'response_datetime': now}})
    return jsonify({'message': 'Response recorded'})


@app.route('/api/request/fetch/<request_id>', methods=['GET'])
def fetch_response(request_id):
    request_data = collection.find_one({'id': request_id})

    if request_data:
        response = request_data['response']
        return jsonify({'response': response})
    else:
        return jsonify({'message': 'Request not found'}), 404


if __name__ == '__main__':
    app.run()
