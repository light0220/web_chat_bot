<!--
 * @作    者 : 北极星光 light22@126.com
 * @创建时间 : 2025-09-16 01:47:52
 * @最后修改 : 2025-09-16 02:10:00
 * @修 改 者 : 北极星光
-->

# web_chat_bot

基于Flask的聊天机器人，使用百度文心一言API实现。

## 功能

- 浏览器访问，可与机器人聊天。
- 可前端自定义机器人人设，包括名称、角色、欢迎语等。
- 聊天记保存到本地json文件，可在前端查看。
- 可前端重置聊天记录。
- 敏感词过滤：过滤掉包含敏感词的消息。

## 安装

```
git clone https://github.com/light0220/web_chat_bot.git
```

## 运行

```
pip install -r requirements.txt
python ernieAI.py
```

## 浏览器访问

```
http://localhost:5000/
```
