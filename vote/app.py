import os
import socket
from flask import Flask, render_template, request, redirect, url_for
from redis import Redis

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@app.route('/', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        vote_data = request.form['vote']
        redis.rpush('votes', vote_data)
        return redirect(url_for('thank_you'))
    return render_template('index.html', hostname=socket.gethostname())

@app.route('/thanks')
def thank_you():
    return render_template('thanks.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
