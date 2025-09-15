#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import yaml
import requests
import json
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

class ErnieAI:
    def __init__(self,
                 api_key=None,
                 bot_name=None,
                 bot_role=None,
                 welcome_words=None,
                 sensitive_words=None):
        self.api_key = api_key
        self.bot_name = bot_name
        self.bot_role = bot_role
        self.welcome_words = welcome_words
        self.sensitive_words = sensitive_words or []  # 确保是列表
        self.chat_history_path = './chat_history.json'
        self.messages = {
            'default_user': [{
                'role': 'system',
                'content': self.bot_role
            }]
        }
        # 加载已保存的聊天记录
        self.load_chat_history()

    # 加载聊天记录并同步到messages
    def load_chat_history(self):
        if os.path.exists(self.chat_history_path):
            with open(self.chat_history_path, 'r', encoding='utf-8') as f:
                try:
                    saved_messages = json.load(f)
                    # 保留系统设定，合并历史消息
                    self.messages['default_user'] = [self.messages['default_user'][0]] + saved_messages
                except:
                    pass  # 加载失败则使用默认设置

    # 保存messages到文件（过滤掉系统设定）
    def save_chat_history(self):
        # 从第1条开始保存，跳过系统设定（第0条）
        messages_to_save = self.messages['default_user'][1:]
        with open(self.chat_history_path, 'w', encoding='utf-8') as f:
            json.dump(messages_to_save, f, ensure_ascii=False, indent=2)

    # 获取前端显示的聊天记录（转换格式并过滤系统设定）
    def get_display_history(self):
        display_history = []
        # 从第1条开始处理，跳过系统设定
        for msg in self.messages['default_user'][1:]:
            display_history.append({
                'sender': 'user' if msg['role'] == 'user' else 'bot',
                'text': msg['content'],
                'timestamp': datetime.now().isoformat()
            })
        return display_history

    # 文本生成
    def ernie_text_generate(self, text, model_name, user='default_user'):
        if user not in self.messages:
            self.messages[user] = [{
                'role': 'system',
                'content': self.bot_role
            }]
        
        # 添加用户消息
        self.messages[user].append({'role': 'user', 'content': text})
        
        # 过滤敏感词
        if any(word in text for word in self.sensitive_words):
            response = '消息中含有敏感词，请重新输入。'
            self.messages[user].append({'role': 'assistant', 'content': response})
            self.save_chat_history()  # 保存记录
            return response

        # 调用API生成回复
        url = "https://qianfan.baidubce.com/v2/chat/completions"
        payload = json.dumps({
            "model": model_name,
            "messages": self.messages[user],  # 包含系统设定的完整消息
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        bot_response = response.json().get('choices')[0].get('message').get('content')
        
        # 添加机器人回复
        self.messages[user].append({'role': 'assistant', 'content': bot_response})
        
        # 保存聊天记录（会自动过滤系统设定）
        self.save_chat_history()
        
        return bot_response

    # 重置消息记录
    def reset_messages(self, user='default_user'):
        self.messages[user] = [{
            'role': 'system',
            'content': self.bot_role
        }]
        # 清空聊天记录文件
        self.save_chat_history()


app = Flask(__name__, static_folder='.')
CORS(app)

# 初始化ErnieAI实例
with open('./config/ernie_config.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
api_key = cfg.get('api_key')
bot_name = cfg.get('bot_name')
bot_role = cfg.get('bot_role')
welcome_words = cfg.get('welcome_words', '')
model_name_text_generate = cfg.get('model_name_text_generate')
# 从配置文件加载敏感词，不允许前端修改
sensitive_words = cfg.get('sensitive_words', [])
ernie_ai = ErnieAI(api_key, bot_name, bot_role, welcome_words, sensitive_words)

# 静态文件路由
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/get_config', methods=['GET'])
def get_config():
    return jsonify({
        'bot_name': bot_name,
        'bot_role': bot_role,
        'welcome_words': welcome_words,
        'model_name_text_generate': model_name_text_generate,
        'sensitive_words': sensitive_words  # 可以获取但不允许修改
    })

# 获取聊天历史（供前端显示）
@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    history = ernie_ai.get_display_history() or []
    return jsonify({'history': history})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    response = ernie_ai.ernie_text_generate(message, model_name_text_generate)
    return jsonify({'response': response})

@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    ernie_ai.reset_messages()
    return jsonify({'status': 'success'})

@app.route('/save_config', methods=['POST'])
def save_config():
    data = request.get_json()
    global bot_name, bot_role, welcome_words, model_name_text_generate
    
    # 读取原始配置文件内容（保留注释和结构）
    with open('./config/ernie_config.yaml', 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    # 需要更新的字段
    update_fields = {
        'bot_name': data.get('bot_name', bot_name),
        'bot_role': data.get('bot_role', bot_role),
        'welcome_words': data.get('welcome_words', welcome_words),
        'model_name_text_generate': data.get('model_name_text_generate', model_name_text_generate)
    }
    
    # 逐行更新配置文件，保留注释和结构
    new_lines = []
    for line in original_lines:
        # 检查是否是需要更新的配置项
        updated = False
        for key, value in update_fields.items():
            # 匹配键名（考虑可能的空格）
            if line.strip().startswith(f'{key}:'):
                # 保留原始缩进
                indent = line[:len(line) - len(line.lstrip())]
                # 处理字符串值，特别是包含换行的bot_role
                if isinstance(value, str) and '\n' in value:
                    # 多行字符串处理（YAML块格式）
                    new_lines.append(f'{indent}{key}: |\n')
                    for line_part in value.split('\n'):
                        new_lines.append(f'{indent}  {line_part}\n')
                else:
                    # 普通值处理
                    new_lines.append(f'{indent}{key}: {value}\n')
                updated = True
                break
        if not updated:
            # 不是需要更新的行，保留原样
            new_lines.append(line)
    
    # 保存更新后的配置
    with open('./config/ernie_config.yaml', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # 更新全局变量
    bot_name = update_fields['bot_name']
    bot_role = update_fields['bot_role']
    welcome_words = update_fields['welcome_words']
    model_name_text_generate = update_fields['model_name_text_generate']
    
    # 更新AI实例配置
    ernie_ai.bot_name = bot_name
    ernie_ai.bot_role = bot_role
    ernie_ai.welcome_words = welcome_words
    ernie_ai.reset_messages()  # 重置消息以应用新的系统设定
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)