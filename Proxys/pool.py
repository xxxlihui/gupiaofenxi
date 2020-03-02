import threading
import time
import requests
from Proxys import header

lock = threading.Lock()
lock2 = threading.Lock()
# {"ip":addr}
addrs = {}
removes = {}
toaddaddrs = []


def addasync(addr: dict):
    toaddaddrs.append(addr)


def add(addr: dict):
    if checkIp(addr):
        _add(addr)


def addUnremoveasync(addr: dict):
    lock.acquire()
    if addr["ip"] in removes:
        return
    lock.release()
    toaddaddrs.append(addr)


def addUnremove(addr: dict):
    lock.acquire()
    if addr["ip"] in removes:
        return
    lock.release()
    if checkIp(addr):
        _add(addr)


def _add(addr: dict):
    lock.acquire()
    addrs[addr["ip"]] = addr
    lock.release()


def remove(ip: str):
    lock.acquire()
    del addrs[ip]
    removes[ip] = None
    lock.release()


def _addUnremove(addr: dict):
    lock.acquire()
    if addr["ip"] in removes:
        return
    addrs[addr["ip"]] = addr
    lock.release()


# 每一个网站使用一次该ip就不能继续使用 TODO 未做
"""
策略使用方式，每个ip多长时间可以使用一次
users={"ip":最后使用时间}
interval 多少秒后能再次使用 
"""


def getOne(users: {} = {}, interval: int = 60):
    lock.acquire()
    for _, v in addrs:
        lasttime = users.get(v["ip"], default=None)
        if lasttime == None:
            users[v["ip"]] = time.time()
            return v
        else:
            if time.time() - lasttime > 60:
                users[v["ip"]] = time.time()
                return v
    lock.release()
    return None


def getProxy(users: {} = {}, interval: int = 60):
    addr = getOne(users, interval)
    if addr == None:
        return {}
    proto, ip, port = addr
    if proto == "HTTP":
        return {"http": "http://" + ip + ":" + port}
    else:
        return {"https:": "https://" + ip + ":" + port}


def checkIp(addr):
    proto, ip, port = addr
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        thiProxy = proto + "://" + ip + ":" + port
        # print(thisIP)
        res = requests.get(url="http://icanhazip.com/",
                           timeout=6, headers=header.getHeader(),
                           proxies={"http": thiProxy})
        proxyIP = res.text
        return proxyIP == ip
    except:
        print("代理IP无效！")
        return False


started = False


def loop():
    while True:
        try:
            addr = toaddaddrs.pop()
            if checkIp(addr):
                _add(addr)
        except:
            time.sleep(2)


# 开始检测线程，检测ip是否有效
def startCheckIp():
    lock2.acquire()
    if started == True:
        return
    started = True
    lock2.release()
    threading.Thread(loop).start()
    return
