import userAgens


def getHeader(refer: str=""):
    return {
        "User-Agent": userAgens.get(),
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Referer": refer,
    }
