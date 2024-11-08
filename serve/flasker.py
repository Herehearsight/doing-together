import json
from os import path, mkdir
from flask import Flask, request, url_for, render_template, send_from_directory, jsonify
import os
from flask_cors import CORS
from pynput.keyboard import Key, Controller

app = Flask(__name__)
# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')

IMAGE_FOLDER = 'static/images'
if not path.exists(IMAGE_FOLDER):
    mkdir(IMAGE_FOLDER)

def st():
    app.run(host='0.0.0.0', port=5050)


@app.route('/')
def index():
    base_url = url_for('serve_image', filename='', _external=True)[:-1]  # 获取基础 URL
    categories = [d for d in os.listdir(IMAGE_FOLDER) if os.path.isdir(os.path.join(IMAGE_FOLDER, d))]
    return render_template('index.html', base_url=base_url, categories=categories)

@app.route('/upload', methods=['POST'])
def upload():
    # 从请求中获取 JSON 数据
    json_data = json.loads(request.form.get('data'))
    username = json_data.get('username')
    filename = json_data.get('filename')

    # 创建用户特定的目录（如果不存在）
    user_directory = os.path.join(IMAGE_FOLDER, username)
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    # 保存图片
    image = request.files['image']
    image.save(os.path.join(user_directory, filename))
    print(username, 'save ok')
    return "上传成功"

@app.route('/categories')
def categories():
    return [d for d in os.listdir(IMAGE_FOLDER) if os.path.isdir(os.path.join(IMAGE_FOLDER, d))]

@app.route('/get_images/<category>')
def get_images(category):
    category_path = os.path.join(IMAGE_FOLDER, category)
    if os.path.exists(category_path):
        images = os.listdir(category_path)
        return jsonify(images)
    else:
        return jsonify([])

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
    # app.run(port=5050)
