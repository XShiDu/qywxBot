import time
from flask import Flask, request
import yaml
import threading
from CheckURL import checkURL
from chat import Chat
from WXBizMsgCrypt3 import WXBizMsgCrypt
from xml.dom.minidom import parseString

bot_config_path = '../config/model_config.yaml'
app_config_path = '../config/qywx_config.yaml'

mybot = Chat(bot_config_path, app_config_path)

app = Flask(__name__)

@app.route("/wecom", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return checkURL(request)
    elif request.method == "POST":
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        data = request.data.decode('utf-8')
        ret, sMsg = WXBizMsgCrypt(mybot.app.Token, mybot.app.EncodingAESKey, mybot.app.corpid).DecryptMsg(data, msg_signature, timestamp, nonce)

        if (ret != 0):
            print("ERR: DecryptMsg ret: " + str(ret))
            return ("failed")
        else:
            doc = parseString(sMsg)
            collection = doc.documentElement
            name_xml = collection.getElementsByTagName("FromUserName")
            msg_xml = collection.getElementsByTagName("Content")
            type_xml = collection.getElementsByTagName("MsgType")
            pic_xml = collection.getElementsByTagName("PicUrl")
            msg_type = type_xml[0].childNodes[0].data
            if msg_type == "text":  # 文本消息
                name = name_xml[0].childNodes[0].data  # 发送者id
                msg = msg_xml[0].childNodes[0].data  # 发送的消息内容

                # 创建子线程，通过子线程生成回答并回复给用户
                sub_thread = threading.Thread(target=mybot.reply, args=(name,msg,))
                sub_thread.start()
                # 主线程等待子线程4秒
                sub_thread.join(2)
                # 若此回复四秒内运行不完
                # if sub_thread.is_alive():
        return ""

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=6363)

