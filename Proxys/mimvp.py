"""
https://proxy.mimvp.com/freeopen.php?proxy=in_hp
in_hp
out_hp
"""
import requests
from pyquery import PyQuery as jq
from Proxys import pool
from Proxys import header
from PIL import Image
import io
import pytesseract

_users = {}
interval = 60


def getProxy():
    addr = pool.getOne(_users, interval)
    if addr == None:
        return {}
    proto = addr["proto"]
    ip = addr["ip"]
    port = addr["port"]
    if proto == "HTTP":
        return {"http": "http://" + ip + ":" + port}
    else:
        return {"https:": "https://" + ip + ":" + port}


def getData(type: str):
    url = "https://proxy.mimvp.com/freeopen.php?proxy=" + type
    proxy = getProxy()
    with requests.get(url=url, proxies=proxy,
                      headers=header.getHeader("https://proxy.mimvp.com/freesecret.php")) as rsp:
        trs = jq(rsp.text)("table.mimvp-tbl.free-proxylist-tbl>tbody>tr").items()
    for tr in trs:
        tds = tr("td")
        ip = tds.eq(1).text()
        if ip == "": continue
        portSrc = "https://proxy.mimvp.com/" + tds.eq(2)("img").attr("src")
        with requests.get(portSrc, proxies=proxy, headers=header.getHeader(url)) as rsp:
            port = pytesseract.image_to_string(Image.open(io.BytesIO(rsp.content)), lang="num")
        proto = tds.eq(3).text()
        if proto.index("HTTP") > -1:
            proto = "HTTP"
        elif proto.index("HTTPS") > -1:
            proto = "HTTPS"
        else:
            continue
        addr = {"ip": ip, "port": port, "proto": proto}
        pool.addUnremove(addr)
        return


getData("in_hp")
getData("out_hp")
