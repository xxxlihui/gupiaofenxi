import platform
import shutil

import pandas as pd
import numpy as np
import os
import pandas as pd
import numpy as np
from struct import unpack

dataDir = '/media/e/tdx/xx'
dataDirTarget = '/media/e/tdx/fxx'
if platform.system() == 'Windows':
    dataDir = 'E:\\projects\\gupiaofenxi\\tdx'
    dataDirTarget = 'E:\\projects\\gupiaofenxi\\tdxx'

files = os.listdir(dataDir)


# 将通达信的日线文件转换成CSV格式

def yuchuli(df):
    # 幅度
    df['涨幅'] = ((df['close'] - df.shift(1)['close']) / df.shift(1)['close']).round(4)
    df['max'] = (df.shift(1)['close'] * 1.1).round(2)
    df['min'] = (df.shift(1)['close'] * 0.9).round(2)
    df['涨停'] = 0  ##涨停标识
    df['跌停'] = 0  ##涨停标识
    df['连涨天数'] = 0  ##连续涨停天数
    df['破板'] = 0  ##破板
    df['大肉'] = 0
    df['大面'] = 0
    df['成交额大于20亿'] = 0
    m = df.shape[0] - 1
    while m > -1:
        r = df.iloc[m]
        m = m - 1
        if r['close'] >= r['max']:
            '''涨停'''
            df.loc[r.name, '涨停'] = 1
        if r['close'] <= r['min']:
            ##跌停
            df.loc[r.name, '跌停'] = 1
        if r['high'] >= r['max'] and r['close'] < r['high']:
            df.loc[r.name, '破板'] = 1
        if r['close'] >= r['max'] or (r['close'] - r['low']) / r['low'] >= 0.1:
            # 涨停 (最高价-收盘价)/收盘价>=0.1
            df.loc[r.name, '大肉'] = 1
        if r['close'] <= r['min'] or (r['high'] - r['close']) / r['close'] >= 0.1:
            # 涨停 (最高价-收盘价)/收盘价>=0.1
            df.loc[r.name, '大面'] = 1
        if r['amount'] >= 20 * 10000 * 10000:
            df.loc[r.name, '成交额大于20亿'] = 1
    return


##连续涨停天数统计
def lxzt(df):
    m = df.shape[0] - 1
    while m > -1:
        r = df.iloc[m]
        m = m - 1
        if r['涨停'] == 1:
            ##涨停
            k = m
            while k > -1:
                rk = df.iloc[k]
                k = k - 1
                if rk['涨停'] == 0:
                    break
            df.loc[r.name, '连涨天数'] = m - k

    return


def chuli():
    for file in files:
        if file.startswith("."): continue
        ph = dataDir + "/" + file
        tph = dataDirTarget + "/" + file
        print(ph)
        df = pd.read_csv(ph, index_col=0, delimiter=",")
        yuchuli(df)
        lxzt(df)
        df.to_csv(tph)


def copy(src, target):
    filelist = os.listdir(src)
    for f in filelist:
        if os.path.exists(target + os.sep + f):
            os.remove(target + os.sep + f)
        shutil.copy(src + os.sep + f, target + os.sep + f)


def fenxi():
    ##统计分析
    import datetime

    start = datetime.date(2020, 3, 10)
    end = datetime.date.today()
    files = os.listdir(dataDirTarget)
    dfs = []
    for f in files:
        tph = dataDirTarget + "/" + f
        dfs.append({"name": f, "data": pd.read_csv(tph, index_col=0, delimiter=",")})
        print(tph)
    # 连板数 key=连板数 value=[]列表
    lx = {}

    startInt = start.year * 10000 + start.month * 100 + start.day
    for d in dfs:
        print(d['name'])
        v = d['name']
        if v.startswith("sh"):
            v = "1" + v[2:8]
        else:
            v = '0' + v[2:8]
        p = d['data']
        try:
            r = p.loc[startInt]
            t = int(r['连涨天数'])
            if t > 0:
                d = lx.get(t)
                if d is None:
                    d = [v]
                    lx[t] = d
                else:
                    d.append(v)
        except:
            continue
    tdir = "/media/e/tdx/l"
    if platform.system() == 'Windows':
        tdir = "E:\\projects\\gupiaofenxi\\l"
    cddp_file = open(tdir + "/CDDP.blk", 'w')
    for i in range(1, 11):
        target_file = open(tdir + "/L" + str(i) + ".blk", 'w')
        ls = lx.get(i)
        if ls != None:
            for k in ls:
                target_file.write(k)
                target_file.write("\n")
                cddp_file.write(k)
                cddp_file.write("\n")
        target_file.close()
    cddp_file.close()
    print(lx)
    if platform.system() == 'Linux':
        d = "/home/li/PycharmProjects/untitled/l"
        copy(tdir, d)
    else:
        d = "C:\\new_dgzq_v6\\T0002\\blocknew"
        copy(tdir, d)


chuli()
fenxi()
