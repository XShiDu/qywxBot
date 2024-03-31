# -*- encoding:utf-8 -*-
import os
import time
import requests
import json
from requests_toolbelt import MultipartEncoder
import yaml

class Push:
    def __init__(self, app_config_path):
        app_config = self.get_config(app_config_path)
        self.agentid = app_config['AgentId']
        self.corpsecret = app_config['Secret']
        self.corpid = app_config['corpid']
        self.URL = app_config['URL']
        self.Token = app_config['Token']
        self.EncodingAESKey = app_config['EncodingAESKey']

        self.access_token, self.expires_in, self.get_time = self.init_access_token()

    def get_config(self, app_config_path):

        with open(app_config_path, 'r', encoding='utf-8') as f:
            app_config = yaml.load(f.read(), Loader=yaml.FullLoader)
        f.close()
        return app_config

    def init_access_token(self):
        response = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=self.corpid, corpsecret=self.corpsecret))
        data = json.loads(response.text)
        access_token = data['access_token']
        expires_in = data['expires_in']
        return access_token, expires_in, time.time()

    def updata_access_token(self):
        # 检查token有没有过期
        time_diff = time.time() - self.get_time
        if time_diff > self.expires_in:
            response = requests.get(
                "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                    corpid=self.corpid, corpsecret=self.corpsecret))
            data = json.loads(response.text)
            access_token = data['access_token']
            expires_in = data['expires_in']
            self.access_token, self.expires_in, self.get_time = access_token, expires_in, time.time()

        # 上传临时文件素材接口，图片也可使用此接口，20M上限
    def post_file(self, filepath, filename):
        response = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=self.corpid, corpsecret=self.corpsecret))
        data = json.loads(response.text)
        access_token = data['access_token']

        post_file_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=file".format(
            access_token=access_token)

        m = MultipartEncoder(
            fields={'file': (filename, open(rf'{filepath}/{filename}', 'rb'), 'multipart/form-data')},
        )
        os.remove(rf'{filepath}/{filename}')

        r = requests.post(url=post_file_url, data=m, headers={'Content-Type': m.content_type})
        js = json.loads(r.text)
        # print("upload " + js['errmsg'])
        if js['errmsg'] != 'ok':
            return None
        return js['media_id']

    # 向应用发送图片接口，_message为上传临时素材后返回的media_id
    def send_img(self, filepath, filename, useridlist=['name1|name2']):
        _message = self.post_file(filepath, filename)
        useridstr = "|".join(useridlist)
        self.updata_access_token()

        json_dict = {
            "touser": useridstr,
            "msgtype": "image",
            "agentid": self.agentid,
            "image": {
                "media_id": _message,
            },
            "safe": 0,
            "enable_id_trans": 1,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        json_str = json.dumps(json_dict)
        response_send = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
                access_token=self.access_token), data=json_str)
        # print("send to " + useridstr + ' ' + json.loads(response_send.text)['errmsg'])
        return json.loads(response_send.text)['errmsg'] == 'ok'

    # 向应用发送文字消息接口，_message为字符串
    def send_text(self, _message, useridlist=['name1|name2']):
        useridstr = "|".join(useridlist)  # userid 在企业微信-通讯录-成员-账号
        self.updata_access_token()
        json_dict = {
            "touser": useridstr,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": _message
            },
            "safe": 0,
            "enable_id_trans": 1,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        json_str = json.dumps(json_dict)
        response_send = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
                access_token=self.access_token), data=json_str)
        # print("send to " + useridstr + ' ' + json.loads(response_send.text)['errmsg'])
        return json.loads(response_send.text)['errmsg'] == 'ok'
