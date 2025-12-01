import os
import socket
from flask import Flask, render_template, request, jsonify
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        vote_data = request.form['vote']
        redis.rpush('votes', vote_data)
        return jsonify({'message': 'Vote recorded successfully!'})
    return render_template('index.html', hostname=socket.gethostname())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
