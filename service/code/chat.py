from chatbot import ChatBot
from qywx_push import Push
from lxml import etree
import threading
import os

class Chat:
    def __init__(self, bot_config_path, app_config_path):
        self.bot = ChatBot(bot_config_path)
        self.app = Push(app_config_path)

    def reply(self, name, msg):
        thread_id = threading.get_ident()
        res = self.bot.reply(name, msg)
        png_ = f'../temp/{thread_id}.png'
        if os.path.exists(png_):
            self.app.send_img('../temp', f'{thread_id}.png', [name])
        else:
            self.app.send_text(res, [name])

# bot_config_path = '../../config/model_config.yaml'
# app_config_path = '../../config/qywx_config.yaml'
#
# mybot = Chat(bot_config_path, app_config_path)
# mybot.reply('sss', '查看大理药业的当前股价')
