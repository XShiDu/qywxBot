from typing import Optional
from math import sqrt, cos, sin
from langchain.tools import BaseTool
import yaml
import requests
import json
import matplotlib.pyplot as plt
import threading

class StockIndustryTool(BaseTool):
    name = "Get stock industry"
    description = ("use this tool when you want to inquire about the industry, concept, and sector corresponding to a specific stock."
                   "To use the tool, you must provide the parameters:`name_with_code`"
                   "The input to this tool should be a comma separated list of a stock name or stock code and a A flag variable to indicate whether it is a stock name or a stock code, with a value of `1` for names and `0` for codes"
                   "For example, the input should be like `000001,0` or `大理药业,1`."
                   )

    def _run(self, name_with_code):
        code, iscode = name_with_code.split(',')[0], name_with_code.split(',')[1][0]
        if code and iscode:
            with open('../data/stocksNameCode.yml', 'r', encoding='utf-8') as f:
                stock_map = yaml.load(f.read(), Loader=yaml.FullLoader)
            f.close()
            with open('../config/api_config.yaml', 'r', encoding='utf-8') as f:
                apis = yaml.load(f.read(), Loader=yaml.FullLoader)
            f.close()
            if iscode == '1':
                code = stock_map[code]
            url = f"{apis['stock_params']['stock_industry']}/{code}/{apis['stock_params']['licence']}"
            response = requests.get(url)
            if response.status_code == 200:
                conception = json.loads(response.text)
                res = f'{code}所属概念或行业包括：\n'
                for index, industry in enumerate(conception):
                    res += f"{index + 1}、{industry['name']}\n"
                return res + '\n请将这些概念直接按原格式回复给用户，不需要进行归纳总结'
            else:
                return "The tool has reached its usage limit. Please reply to the user with" \
                       " 'Please remind the administrator to check the interface status,' and do not reply with anything else."
        else:
            return "Could not get the informations of stocks. Need 'code' and 'iscode' "

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

def plot_today_card(today_price, name, code, path):
    font_ = 'SimHei'
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 100)
    ax.axis('off')

    diff = round(float(today_price['p']) -float(today_price['yc']), 2)
    up = diff >= 0

    ax.text(x=0, y=90, s=f"{name} ({code})", ha='left', va='baseline',
            fontdict=dict(fontsize=22, color='black', family=font_, weight='light'),
            )

    color = 'red' if up else 'green'
    ax.text(x=20, y=70, s=f"{today_price['p']}", ha='left', va='baseline',
            fontdict=dict(fontsize=30, color=color, family=font_, weight='bold'),
            )

    y = (71, 6) if up else (81, -6)
    ax.arrow(20 + (len(today_price['p']) + 1) * 7, y[0], 0, y[1], head_width=5, head_length=4, linewidth=2, width=2, fc=color, ec=color)

    tex = f"{diff} {today_price['pc']}%" if up else f"{diff} {today_price['pc']}%"
    ax.text(x=20, y=60, s=tex, ha='left', va='baseline',
            fontdict=dict(fontsize=15, color=color, family=font_, weight='light'),
            )

    ax.text(x=0, y=45, s=f"今开：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    o_color = 'red' if float(today_price['o']) - float(today_price['yc']) >= 0 else 'green'
    ax.text(x=15, y=45, s=f"{today_price['o']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color=o_color, family=font_, weight='light'),
            )
    ax.text(x=35, y=45, s=f"最高：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    h_color = 'red' if float(today_price['h']) - float(today_price['yc']) >= 0 else 'green'
    ax.text(x=50, y=45, s=f"{today_price['h']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color=h_color, family=font_, weight='light'),
            )
    ax.text(x=70, y=45, s=f"换手：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=85, y=45, s=f"{today_price['hs']}%", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=105, y=45, s=f"成交量：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=125, y=45, s="{:.2f}万".format(float(today_price['v']) / 10000), ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )

    ax.text(x=0, y=35, s=f"昨收：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=15, y=35, s=f"{today_price['yc']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=35, y=35, s=f"最低：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    l_color = 'red' if float(today_price['l']) - float(today_price['yc']) >= 0 else 'green'
    ax.text(x=50, y=35, s=f"{today_price['l']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color=l_color, family=font_, weight='light'),
            )
    ax.text(x=70, y=35, s=f"量比：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=85, y=35, s=f"{today_price['lb']}%", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=105, y=35, s=f"成交额：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=125, y=35, s="{:.2f}亿".format(float(today_price['cje']) / 100000000), ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )

    ax.text(x=0, y=25, s=f"总市值：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=20, y=25, s="{:.2f}亿".format(float(today_price['sz']) / 100000000), ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=60, y=25, s=f"流通市值：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=85, y=25, s="{:.2f}亿".format(float(today_price['sz']) / 100000000), ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )

    ax.text(x=0, y=15, s=f"市盈率：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=20, y=15, s=f"{today_price['pe']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=60, y=15, s=f"市净率：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=85, y=15, s=f"{today_price['sjl']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )

    ax.text(x=0, y=5, s=f"时间：", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    ax.text(x=15, y=5, s=f"{today_price['t']}", ha='left', va='baseline',
            fontdict=dict(fontsize=12, color='black', family=font_, weight='light'),
            )
    plt.savefig(path, bbox_inches="tight", pad_inches=0.1)
    plt.close()

class StockPriceTool(BaseTool):
    name = "Get stock price"
    description = ("use this tool when you want to get the current stock price."
                   "To use the tool, you must provide the parameters:`name_with_code`"
                   "The input to this tool should be a comma separated list of a stock name or stock code and a A flag variable to indicate whether it is a stock name or a stock code, with a value of `1` for names and `0` for codes"
                   "For example, the input should be like `000001,0`、`000636,0` or `大理药业,1`、`长安汽车,1`."
                   )

    def _run(self, name_with_code):
        code, iscode = name_with_code.split(',')[0], name_with_code.split(',')[1][0]
        if '`' in code or "'" in code or '‘' in code:
            code = code[1:]
        if code and iscode:
            with open('../data/stocksNameCode.yml', 'r', encoding='utf-8') as f:
                stock_name_map = yaml.load(f.read(), Loader=yaml.FullLoader)
            f.close()
            with open('../data/stocksCodeName.yml', 'r', encoding='utf-8') as f:
                stock_code_map = yaml.load(f.read(), Loader=yaml.FullLoader)
            f.close()
            with open('../config/api_config.yaml', 'r', encoding='utf-8') as f:
                apis = yaml.load(f.read(), Loader=yaml.FullLoader)
            f.close()
            if iscode == '1':
                stock_mc = code
                stock_dm = stock_name_map[code]
            else:
                stock_mc = stock_code_map[code]
                stock_dm = code
            today_price_url = f"{apis['stock_params']['today_price']}/{stock_dm}/{apis['stock_params']['licence']}"
            response = requests.get(today_price_url)
            if response.status_code == 200:
                today_price = json.loads(response.text)
                name = threading.get_ident()
                imgpath = f'../temp/{name}.png'
                plot_today_card(today_price, stock_mc, stock_dm, imgpath)
                return f"{stock_mc}股价，为{today_price['p']}元"
            else:
                return "The tool has reached its usage limit. Please reply to the user with" \
                       " 'Please remind the administrator to check the interface status,' and do not reply with anything else."
        else:
            return "Could not get the informations of stocks. Need 'code' and 'iscode' "

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")



