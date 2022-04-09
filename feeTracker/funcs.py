import json
import time
import requests
from datetime import datetime
import os
import sqlite3
import random


def get_transactions():
    url = 'https://mempool.space/api/mempool/recent'
    response = requests.get(url)
    transactions = response.json()

    if (transactions):
        for i in range(len(transactions)):
            for k in range(len(transactions)):
                if (transactions[i]['vsize']):
                    transactions[k]["feeRate"] = transactions[k]["fee"] / transactions[i]["vsize"]
                else:
                    transactions[k]["feeRate"] = transactions[k]["fee"] / transactions[i]["size"]
            for j in range(0, len(transactions) - i - 1):
                if (transactions[j]["feeRate"] < transactions[j + 1]["feeRate"]):
                    a = transactions[j]
                    transactions[j] = transactions[j + 1]
                    transactions[j + 1] = a

        if os.stat('mempool1.json').st_size == 0:
            with open('mempool1.json', 'w') as m:
                json.dump(transactions, m, indent=4)
        else:
            with open('mempool2.json', 'w') as m:
                json.dump(transactions, m, indent=4)

        with open('mempool1.json', 'r') as f:
            mempool1 = json.load(f)

        if os.stat('mempool2.json').st_size != 0:
            with open('mempool2.json', 'r') as f:
                mempool2 = json.load(f)

            for i in range(len(mempool2)):
                mempool1.append(mempool2[i])

            for i in range(len(mempool1)):
                for j in range(0, len(mempool1) - i - 1):
                    if mempool1[j]['feeRate'] < mempool1[j + 1]['feeRate']:
                        a = mempool1[j]
                        mempool1[j] = mempool1[j + 1]
                        mempool1[j + 1] = a

        Mempool = []
        for i in range(len(mempool1) - 1):
            if mempool1[i]['txid'] != mempool1[i + 1]['txid']:
                Mempool.append(mempool1[i])

        with open('mempool1.json', 'w') as m:
            json.dump(Mempool, m, indent=4)

    else:
        print("NO NEW TRANSACTIONS!")

    response.close()



def max_feeRate():  # максимальный feeRate
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    maxFeeRate = 0
    for i in range(len(Mempool)):
        if Mempool[i]['feeRate'] > maxFeeRate:
            maxFeeRate = Mempool[i]['feeRate']

    return maxFeeRate


def int_r(n):
    n = int(n + (0.5 if n > 0 else -0.5))
    return n


def avg_feeRate():  # средний feeRate
    # with open('mempool1.json', 'r') as f:
    #     Mempool = json.load(f)
    #
    # last = near_block_min_fee_position()
    # sum_s = 0
    # sum_f = 0
    # for i in range(last):
    #     sum_s += Mempool[i]['vsize']
    #     sum_f += Mempool[i]['fee']
    # avg_feeRate = sum_f / sum_s
    # return avg_feeRate
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    avg = int_r(Mempool[1500]['feeRate'])
    return avg


def sum_size():  # вес всего мемпула
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
        sum = 0
    for i in range(len(Mempool)):
        sum += Mempool[i]['vsize']
    return sum


def near_block_min_fee():  # минимальный feeRate транзакции, попадающей в блок последней
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    nearBlockMinFee_number = 0
    sum = 0
    oneBlockSize = 1000000
    for i in range(len(Mempool)):
        sum += Mempool[i]['vsize']
        if sum <= oneBlockSize:
            nearBlockMinFee_number = i
    last = Mempool[nearBlockMinFee_number]['feeRate']  # fee последней транзакции, котроая войдет в блок
    return last


def near_block_min_fee_position():  # номер транзакции с минимальным feeRate, которая попадет в блок
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    nearBlockMinFee_number = 0
    sum = 0
    oneBlockSize = 1000000
    for i in range(len(Mempool)):
        sum += Mempool[i]['vsize']
        if sum <= oneBlockSize:
            nearBlockMinFee_number = i
    return nearBlockMinFee_number


def amount_of_transactions():  # количество транзакций в пуле
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    count = 0
    for i in range(len(Mempool)):
        count += 1
    return count


def mine_block():  # первые тракзакции с наибольшим feeRate и сумма которых = 1Мб отправляем в блок(просто удаляем, чтобы счиатть дальше)
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
    pool = []
    last = near_block_min_fee_position()
    for i in range(last, len(Mempool)):
        pool.append(Mempool[i])
    with open('mempool1.json', 'w') as m:
        json.dump(pool, m, indent=4)


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
    with open('mempool1.json', 'r') as f:
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
    with open('mempool1.json', 'w') as m:
        json.dump(txsParams, m, indent=4)


# def compare():
#     com = []
#     with open('Mempool_id.json', 'r') as f:
#         mempoolTxIds = json.load(f)
#     with open('Mempool.json', 'r') as f:
#         Mempool = json.load(f)
#     for i in range(len(Mempool)):
#         if mempoolTxIds.count(Mempool[i]["txid"]) != 0:
#             com.append(Mempool[i])
#     with open('Mempool.json', 'w') as m:
#         json.dump(com, m, indent=4)
#     with open('mempool1.json', 'w') as m:
#         json.dump(com, m, indent=4)