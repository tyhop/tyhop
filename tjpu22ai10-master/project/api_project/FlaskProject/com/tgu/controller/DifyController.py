import requests
from flask import Blueprint, request, jsonify

dify = Blueprint('dify', __name__)
url = 'http://192.168.10.128/v1/workflows/run'


@dify.route('/delay', methods=['POST'])
def delayDevice():

    api_key = 'app-IGJCXsiW0Wuw040GQ14FOFGL'

    result = request.json

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'inputs': {
            "place": result['question']
        },
        'user': 'crab'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to run workflow",
                        'status_code': response.status_code,
                        'message': response.text
                        },500)

@dify.route('/baggage', methods=['POST'])
def baggageDevice():

    api_key = 'app-4oGe9OCgzRZEdB9jlo7KQja0'

    result = request.json
    baggage_list = result['content']
    baggage_type = result['type']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'inputs': {
            'baggage_list': baggage_list,
            "baggage_type": baggage_type
        },
        'user': 'crab'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to run workflow",
                        'status_code': response.status_code,
                        'message': response.text
                        },500)

@dify.route('/weather', methods=['POST'])
def weatherDevice():

    api_key = 'app-6LLlF6vTf9IpyHSPr3sgDjy7'

    result = request.json

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'inputs': {
            "place": result['question']
        },
        'user': 'crab'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to run workflow",
                        'status_code': response.status_code,
                        'message': response.text
                        },500)

@dify.route('/travel', methods=['POST'])
def travelDevice():

    api_key = 'app-g6AtVbu1Nw5VYkpL1qoRm32H'

    result = request.json

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'inputs': {
            "destination": result['question']
        },
        'user': 'crab'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to run workflow",
                        'status_code': response.status_code,
                        'message': response.text
                        },500)


@dify.route('/food', methods=['POST'])
def foodDevice():

    api_key = 'app-DKHCj9SsjD797QsH3lJl1VSa'

    result = request.json

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'inputs': {
            "place": result['question']
        },
        'user': 'crab'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to run workflow",
                        'status_code': response.status_code,
                        'message': response.text
                        },500)
