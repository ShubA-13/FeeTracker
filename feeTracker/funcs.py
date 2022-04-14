import json
import time
import requests
from datetime import datetime
import os
import sqlite3
import random


def get_transactions():
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Send request https://mempool.space/api/mempool/recent')
    url = 'https://mempool.space/api/mempool/recent'
    response = requests.get(url)
    transactions = response.json()

    if (transactions):
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Receive response OK')
        for i in range(len(transactions)):
            transactions[i]["feeRate"] = transactions[i]["fee"] / transactions[i]["vsize"]

        if os.stat('mempool.json').st_size == 0:
            with open('mempool.json', 'w') as m:
                json.dump(transactions, m, indent=4)

        else:
            with open('mempool.json', 'r') as f:
                mempool = json.load(f)

            for i in range(len(transactions)):
                mempool.append(transactions[i])

            Mempool = check_same(mempool)

            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs ids cache size', len(Mempool))
            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs cache size', sum_size())

            with open('mempool.json', 'w') as m:
                json.dump(Mempool, m, indent=4)

    else:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Receive error response with 404')

    response.close()


def sort():
    with open('mempool.json', 'r') as f:
        mempool = json.load(f)

    for i in range(len(mempool)):
        for j in range(0, len(mempool) - i - 1):
            if (mempool[j]["feeRate"] < mempool[j + 1]["feeRate"]):
                a = mempool[j]
                mempool[j] = mempool[j + 1]
                mempool[j + 1] = a

    with open('mempool.json', 'w') as m:
        json.dump(mempool, m, indent=4)


def check_same(massive):
    m = []
    for i in range(len(massive) - 1):
        if massive[i]['txid'] != massive[i + 1]['txid']:
            m.append(massive[i])
    return m


def int_r(n):
    n = int(n + (0.5 if n > 0 else -0.5))
    return n


def avg_feeRate():  # средний feeRate
    with open('mempool.json', 'r') as f:
        Mempool = json.load(f)
    avg = int_r(Mempool[1000]['feeRate'])
    return avg


def sum_size():  # вес всего мемпула
    with open('mempool.json', 'r') as f:
        Mempool = json.load(f)
        sum = 0
    for i in range(len(Mempool)):
        sum += Mempool[i]['vsize']
    return sum


def amount_of_transactions():  # количество транзакций в пуле
    with open('mempool.json', 'r') as f:
        Mempool = json.load(f)
    count = 0
    for i in range(len(Mempool)):
        count += 1
    return count


def feeRate_to_db():
    load()
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS avgFee(Date , avg text);""")
    con.commit()
    dt_now = datetime.now()
    t = dt_now.strftime("%Y-%m-%d-%H.%M.%S")
    avg = avg_feeRate()
    mempool()
    p = (t, avg)
    cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
    con.commit()


def load():
    get_transactions()
    block_size = 1000000
    while sum_size() <= block_size:
        get_transactions()
        sort()
        time.sleep(random.uniform(1, 5))


def load_id(par):
    while True:
        if par.value == True:
            url = 'https://mempool.space/api/mempool/txids'
            response = requests.get(url)
            mempoolTxIds = response.json()
            with open('Mempool_id.json', 'w') as m:
                json.dump(mempoolTxIds, m, indent=4)
            response.close()
        time.sleep(60)


def mempool():
    txsParams = []
    with open('Mempool_id.json', 'r') as f:
        mempoolTxIds = json.load(f)
    with open('mempool.json', 'r') as f:
        mempool1 = json.load(f)
    for i in range(len(mempoolTxIds)):
        for j in range(len(mempool1)):
            if mempoolTxIds[i] == mempool1[j]["txid"]:
                txsParams.append(mempool1[j])
    for i in range(len(txsParams)):
        for j in range(0, len(txsParams) - i - 1):
            if txsParams[j]['feeRate'] < txsParams[j + 1]['feeRate']:
                a = txsParams[j]
                txsParams[j] = txsParams[j + 1]
                txsParams[j + 1] = a
    with open('mempool.json', 'w') as m:
        json.dump(txsParams, m, indent=4)
