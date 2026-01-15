# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: MIT

from flask import Flask, request, redirect, make_response, render_template
import redis
import uuid
import config

app = Flask(__name__)

# Redis connection
redis_kwargs = {
    'host': config.REDIS_HOST,
    'port': config.REDIS_PORT,
    'decode_responses': True
}
if config.REDIS_PASSWORD:
    redis_kwargs['password'] = config.REDIS_PASSWORD

r = redis.Redis(**redis_kwargs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form.get('username')
    password = request.form.get('password')
    # Simple user authentication
    users = {
        'user1': 'password1',
        'user2': 'password2'
    }
    if username in users and users[username] == password:
        session_id = str(uuid.uuid4())
        r.setex(session_id, config.SESSION_EXPIRE, username)
        resp = make_response(redirect('/choose'))
        resp.set_cookie('SESSIONID', session_id, max_age=config.SESSION_EXPIRE, httponly=True)
        return resp
    return render_template('login.html', error='Incorrect username or password')

@app.route('/choose')
def choose():
    session_id = request.cookies.get('SESSIONID')
    if not session_id or not r.get(session_id):
        return redirect('/login')
    return render_template('choose.html', server_ip=config.SERVER_HOST)

@app.route('/logout')
def logout():
    session_id = request.cookies.get('SESSIONID')
    if session_id:
        r.delete(session_id)
    resp = make_response('<h3>Logged out successfully, <a href="/login">click here to log in again</a></h3>')
    resp.delete_cookie('SESSIONID')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.AUTH_SERVER_PORT)
