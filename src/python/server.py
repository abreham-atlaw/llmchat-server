from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient('mongodb+srv://abrehamatlaw:kRqIp2ZVP0w4di7T@cluster0.trf60oq.mongodb.net/?retryWrites=true&w=majority')
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

    while True:
        request_data = collection.find_one({'id': request_data['id']})
        if request_data['response']:
            break

    return jsonify({'response': request_data['response']})


@app.route('/api/request/get', methods=['GET'])
def get_request():
    request_data = collection.find_one({'lock_datetime': None, 'response_datetime': None})

    if request_data:
        request_id = request_data['id']
        now = datetime.now()
        collection.update_one({'id': request_id}, {'$set': {'lock_datetime': now}})
        return jsonify(request_data)
    else:
        return jsonify({'message': 'No available requests'})


@app.route('/api/request/respond', methods=['POST'])
def respond_request():
    data = request.get_json()
    request_id = data['id']
    response = data['response']
    now = datetime.now()

    collection.update_one({'id': request_id}, {'$set': {'response': response, 'response_datetime': now}})
    return jsonify({'message': 'Response recorded'})

if __name__ == '__main__':
    app.run()
