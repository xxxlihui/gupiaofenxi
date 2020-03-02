import pandas as pd
import numpy as np
import os
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib as plt

dataDir = '/media/e/tdxg'
dataDirTarget = '/media/e/tdxgs'

files = os.listdir(dataDir)


def yuchuli(df):
    # 幅度
    df['gains'] = ((df['close'] - df.shift(1)['close']) / df.shift(1)['close']).round(4)
    df['max'] = (df.shift(1)['close'] * 1.1).round(2)
    df['min'] = (df.shift(1)['close'] * 0.9).round(2)
    df['涨跌停'] = 0  ##涨停标识
    df['连涨天数'] = 0  ##连续涨停天数
    df['破板'] = 0  ##破板
    m = df.shape[0] - 1
    while m > -1:
        r = df.iloc[m]
        m = m - 1
        if r['close'] == r['max']:
            '''涨停'''
            df.loc[r.name, '涨跌停'] = 1
        if r['close'] == r['min']:
            ##跌停
            df.loc[r.name, '涨跌停'] = -1
        if r['high'] == r['max'] and r['close'] != r['max']:
            df.loc[r.name, '连涨天数'] = 1
    return


##连续涨停天数统计
def lxzt(df):
    m = df.shape[0] - 1
    while m > -1:
        r = df.iloc[m]
        m = m - 1
        if r['涨跌停'] == 1:
            ##涨停
            k = m
            while k > -1:
                rk = df.iloc[k]
                k = k - 1
                if rk['涨跌停'] != 1:
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


def fenxi():
    ##统计分析
    import datetime

    start = datetime.date(2020, 2, 24)
    now = datetime.date.today()
    files = os.listdir(dataDirTarget)
    dfs = []
    for f in files:
        tph = dataDirTarget + "/" + f
        dfs.append({"name": f, "data": pd.read_csv(tph, index_col=0, delimiter=",")})
    # 连板数 key=连板数 value=[]列表
    lx = {}

    while start < now:
        start = start + datetime.timedelta(days=1)
        startInt = start.year * 10000 + start.month * 100 + start.day
        for d in dfs:
            r = d.data.loc[startInt]
            t = r['连涨天数']
            if t > 0:
                if lx.has_key(t):
                    v = lx[t]
                    v.append(r.name)
                else:
                    v = [r.name]
                    lx[t] = v
    print(lx)

