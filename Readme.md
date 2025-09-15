<!--
 * @作    者 : 北极星光 light22@126.com
 * @创建时间 : 2025-09-16 01:47:52
 * @最后修改 : 2025-09-16 02:36:41
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

准备：

- Python 3.6+
- 浏览器：Chrome、Firefox、Safari等
- 百度文心一言apiKey ，获取地址：[https://console.bce.baidu.com/iam/#/iam/apikey/list]()

安装：

```
git clone https://github.com/light0220/web_chat_bot.git
cd web_chat_bot
pip install -r requirements.txt
```

配置：

- 将 `config` 目录下的 `ernie_config - example.yaml` 重命名为 `ernie_config.yaml`。
- 打开 `ernie_config.yaml`，配置 `apiKey`。
- 聊天模型、机器人身份预设等，可在`ernie_config.yaml`中修改，也可以在前端页面修改。
- 敏感词列表根据需要添加。

## 运行

```
python ernieAI.py
```

## 浏览器访问

```
http://localhost:5000
```
