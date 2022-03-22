import json
import requests
from datetime import datetime
import os
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)


def get_transactions():
    url = 'https://mempool.space/api/mempool/recent'
    response = requests.get(url)
    transactions = response.json()

    for i in range(len(transactions)):
        for k in range(len(transactions)):
            now = datetime.datetime.today()
            transactions[k]["date"] = now.strftime("%Y-%m-%d-%H.%M.%S")

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


def max_feeRate(): #максимальный feeRate
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

def avg_feeRate(): #средний feeRate
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
    avg = int_r(Mempool[1000]['feeRate'])
    mine_block()
    return avg

def sum_size(): # вес всего мемпула
    with open('mempool1.json', 'r') as f:
        Mempool = json.load(f)
        sum = 0
    for i in range(len(Mempool)):
        sum += Mempool[i]['vsize']
    return sum


def near_block_min_fee(): #минимальный feeRate транзакции, попадающей в блок последней
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


def near_block_min_fee_position(): #номер транзакции с минимальным feeRate, которая попадет в блок
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


def amount_of_transactions(): #количество транзакций в пуле
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


@app.route('/get_avg', methods=['GET'])
def create():
    load()
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS avgFee(Date , avg text);""")
    con.commit()
    now = datetime.datetime.today()
    t = now.strftime("%Y-%m-%d-%H.%M.%S")
    avg = avg_feeRate()
    p = (t, avg)
    cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
    con.commit()
    response = {
        'date' : t,
        'avg' : avg
    }
    return jsonify(response), 200

@app.route('/fee_in_period', methods=['GET'])
def get_avg_in_period():
    print("high")
    t1 = input() #2022-03-22-23.00.31
    print("low")
    t2 = input() #2022-03-22-21.11.46
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    avgs = """SELECT * from avgFee"""
    cur.execute(avgs)
    data = cur.fetchall()
    for el in data:
        if el[0] <= t1 and el[0] >= t2:
            response = {
                'data' : el[0],
                'avg' : el[1]
            }
            return jsonify(response), 200



def load():
    get_transactions()
    block_size = 1000000
    while sum_size() <= block_size:
        get_transactions()



if __name__ == '__main__':
    # get_transactions()
    # block_size = 1000000
    # while sum_size() <= block_size:
    #     get_transactions()
    # avg = avg_feeRate()
    # print(avg)
    # print(amount_of_transactions())
    app.run(host='0.0.0.0', port=5000)
    #print(amount_of_transactions())

