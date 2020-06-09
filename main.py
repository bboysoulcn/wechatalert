import requests
import logging
import falcon
import json

# 微信机器人链接
wechat_boot_url = ""

# 日志模块
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler('log.log', mode='w', encoding='UTF-8')
fileHandler.setLevel(logging.NOTSET)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


# 处理从alertmanager接收过来的信息
def message_handler(message):
    message = eval(message)
    alerts = message["alerts"]
    alert_message = []
    # 多台机器的时候处理
    for i in range(len(alerts)):
        alert = alerts[i]
        alert = eval(str(alert))
        status = alert["status"]
        labels = alert["labels"]
        annotations = alert["annotations"]
        startsAt = alert["startsAt"]
        endsAt = alert["endsAt"]
        alertname = eval(str(labels))["alertname"]
        instance = eval(str(labels))["instance"]
        status = eval(str(labels))["status"]
        description = eval(str(annotations))["description"]
        message = "------------------------------" + '\n' \
                  + "           告警来了"  + '\n' \
                  + "------------------------------" + '\n' \
                  + "状态: " + status + '\n' \
                  + "告警名字: " + alertname + '\n' \
                  + "告警实例: " + instance + '\n'  \
                  + "告警等级: " + status + '\n' \
                  + "告警描述: " + description + '\n' \
                  + "开始时间: " + startsAt + '\n' \
                  + "结束时间: " + endsAt + '\n' \
                  + "------------------------------"
        alert_message.append(message)
    return alert_message

# 发送到微信里的函数
def send_wechat(message):
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    logger.debug(message)
    body = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    print(str(body))
    requests.post(wechat_boot_url, json.dumps(body), headers=headers)

# alertmanager post请求处理函数
class Connect(object):
    def on_post(self, req, resp):
        messages = req.stream.read()
        logger.debug(messages)
        try:
            messages = str(bytes.decode(messages))
            logger.debug(messages)
            messages = message_handler(messages)
            for i in range(len(messages)):
                send_wechat(str(messages[i]))
        except Exception as e:
            logger.debug(e)



app = falcon.API()
connect = Connect()
app.add_route('/connect', connect)
