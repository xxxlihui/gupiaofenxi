# coding=utf8
'''
爬取东方财富的的质押数据并处理
获取方式
http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=ZD_QL_LB&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=amtshareratio&sr=-1&p=1&ps=50&js=var%20ixpiBKud={pages:(tp),data:(x),font:(font)}&filter=(tdate=%272019-12-13%27)&rt=52556082
http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=ZD_QL_LB&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=amtshareratio&sr=-1&p=3&ps=50&js=var%20yyKPpMMx={pages:(tp),data:(x),font:(font)}&filter=(tdate=%272019-12-13%27)&rt=52560096
http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=ZD_QL_LB&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=amtshareratio&sr=-1&p=1&ps=50&js=var%20ixpiBKud={pages:(tp),data:(x),font:(font)}&filter=(tdate=%272019-12-13%27)&rt=52558881


js=var部分是返回的js的变量定义
rt的只的算法rt=parseInt(parseInt(new Date().getTime()) / 30000)
EM_MutiSvcExpandInterface/api/js/get?type=ZD_QL_LB&token=70f12f2f4f091e459a279469fe49eca5&cmd=&
st={sortType}&sr={sortRule}&p={page}&ps={pageSize}&js=var {jsname}={pages:(tp),data:(x),font:(font)}{param}
'''

import requests
import json
import os
from urllib import request
from datetime import datetime
from datetime import timedelta
from urllib.parse import quote
import time
import string

rawUrl = 'http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get?type=ZD_QL_LB&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st={sortType}&sr={sortRule}&p={page}&ps={pageSize}&js=var%20{jsname}={jsValue}{param}'


# 一共的页数
# 从第二页开始
def getData(date: string, page: int):
    while True:
        try:
            params = {
                "sortType": "amtshareratio",
                "sortRule": "-1",
                "page": page,
                "pageSize": 50,
                "jsname": "ixpiBKud",
                "param": "",
                "jsValue": "{pages:(tp),data:(x),font:(font)}"
            }
            param = {
                "time": date,
                "timeStamp": int(datetime.now().timestamp() * 1000 / 30000)
            }
            print(int(datetime.now().timestamp() * 1000 / 3000))
            rawParamStr = "&filter=(tdate=%27{time}%27)&rt={timeStamp}"
            # rawParamStr = "&filter=(tdate=‘{time}’)&rt={timeStamp}"
            params["param"] = rawParamStr.format(**param)
            url = rawUrl.format(**params)
            print(url)
            with requests.get(url, headers={"Connection": "close"}, verify=False) as req:
                ct = req.text.replace("var ixpiBKud=", "") \
                    .replace("pages:", '"pages":') \
                    .replace("data:", '"data":') \
                    .replace("font:", '"font":')
                print(ct)
                js = json.loads(ct)
                return js
        except:
            sleep(120)


# 读取文件，不存在则创建
def readFile(path: string):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path) as f:
        return f.read()


def writeFile(path: string, content: string):
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, mode="tw+") as f:
        f.write(content)


def getLastTime():
    return readFile("./data/last")


def setLastTime(last: string):
    writeFile("./data/last", last)


def fontMappingToDic(fontmaps: list):
    dic = {}
    for fontmap in fontmaps:
        dic[fontmap['code']] = str(fontmap['value'])
    return dic


def replaceFontmaps(rawstr: str, fontmap: dict):
    for k, v in fontmap.items():
        rawstr = rawstr.replace(k, v)
    return rawstr


def processorData(rawData: dict):
    fontMapping = fontMappingToDic(rawData["font"]["FontMapping"])
    datas = rawData["data"]
    for data in datas:
        toReplaceKeys = ["amtshareratio", "bballowance", "zysz", "amtsharenum", "bbyallowance", "bbwallowance", "zdf"]
        for i in toReplaceKeys:
            data[i] = replaceFontmaps(data[i], fontMapping)


def saveData(data: list, daystr: str):
    with open("./data/" + daystr + ".json", "tw+") as f:
        f.write(json.dumps(data, ensure_ascii=False))


def sleep(se: int = 30):
    time.sleep(se)


last = getLastTime()
if last == "":
    last = datetime.now() + timedelta(days=-360)
else:
    last = datetime.strptime(last, '%Y-%m-%d') + timedelta(days=1)
print(last)
now = datetime.now()
for i in range((now - last).days + 1):
    day = last + timedelta(days=i)
    dayStr = day.strftime('%Y-%m-%d')
    print(dayStr)
    # 获取第一页
    first = getData(dayStr, 1)
    pages = int(first["pages"])
    if pages == 0:
        setLastTime(dayStr)
        sleep()
        continue
    processorData(first)
    data = first["data"]
    sleep()
    # 遍历其他页
    i = 2
    while i <= pages:
        rawData = getData(dayStr, i)
        processorData(rawData)
        data.extend(rawData["data"])
        i = i + 1
        sleep()
    saveData(data, dayStr)
    setLastTime(dayStr)
