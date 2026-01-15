# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: MIT

from flask import Flask, request, redirect, render_template
import redis
import config

app = Flask(__name__)

redis_kwargs = {
    'host': config.REDIS_HOST,
    'port': config.REDIS_PORT,
    'decode_responses': True
}
if config.REDIS_PASSWORD:
    redis_kwargs['password'] = config.REDIS_PASSWORD

r = redis.Redis(**redis_kwargs)

@app.route('/')
def index():
    session_id = request.cookies.get('SESSIONID')
    if not session_id:
        return redirect(f'http://{config.SERVER_HOST}:{config.AUTH_SERVER_PORT}/login')
    username = r.get(session_id)
    if not username:
        return redirect(f'http://{config.SERVER_HOST}:{config.AUTH_SERVER_PORT}/login')
    return render_template('service_b.html', username=username, server_ip=config.SERVER_HOST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.SERVICE_B_PORT)
