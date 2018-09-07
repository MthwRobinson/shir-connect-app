""" Flask app for the TRS Dashboard backend """
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/service/test', methods=['GET'])
def test():
    """ Tests to make sure the flask app is working """
    return jsonify({
        'status': 'success',
        'message': 'Hello, friend! :)'
    })
