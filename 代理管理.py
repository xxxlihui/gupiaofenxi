# https://www.kuaidaili.com/free/inha/1/
import requests
from pyquery import PyQuery as pq
import time
import userAgens


def getData(index: int, proxy: str = ""):
    url = "https://www.kuaidaili.com/free/inha/" + str(index) + "/"
    ips = []
    refer = "https://www.kuaidaili.com/free/inha/" + str(index - 1) + "/"
    if index == 1:
        refer = "https://www.kuaidaili.com/free/inha/1/"
    total = ""
    proxys = {}
    if proxy != "":
        proxys = {"http": proxy, "https:": proxy}
    with requests.get(url, headers={
        "User-Agent": userAgens.get(),
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
        "Referer": refer,
    },
                      proxies=proxys
                      ) as rsp:
        items = pq(rsp.text)("#list >table.table.table-bordered.table-striped>tbody>tr").items()
        for item in items:
            tds = item("td")
            ipStr = tds.eq(0).text()
            port = tds.eq(1).text()
            proc = tds.eq(3).text()
            if proc.find("HTTP") > -1:
                ip = {"proto": "HTTP", "ip": ipStr, "port": port}
            elif proc.find("HTTPS") > -1:
                ip = {"proto": "HTTPS", "ip": ipStr, "port": port}
            if checkIp(ip):
                print(ip, ip, "有效")
                ips.append(ip)
            else:
                print(ip, ip, "无效")
        total = pq(rsp.text)("#listnav>ul>li:last").prev().text()
    print({"page": index, "total": total, "ips": ips})
    time.sleep(10)
    return [ips, total]


def checkIp(ip):
    proto, ip, port = ip
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        thiProxy = proto + "://" + ip + ":" + port
        # print(thisIP)
        res = requests.get(url="http://icanhazip.com/", headers={"UserAgent": userAgens.get()}, timeout=8,
                           proxies={"http": thiProxy})
        proxyIP = res.text
        return proxyIP == ip
    except:
        print("代理IP无效！")
        return False


# 获取第一页
ips, total = getData(1)
i = 2
while i < int(total) + 1:
    _ips, _ = getData(i)
    i = i + 1
    ips.append(_ips)
print(ips, total)
