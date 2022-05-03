import json
import time
import requests
from datetime import datetime
import os
import sqlite3

fee_r = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0,
         11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, '20&More': 0}


def get_transactions_from_MempoolSpace():
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Send request https://mempool.space/api/mempool/recent')
    url = 'https://mempool.space/api/mempool/recent'
    response = requests.get(url)
    transactions = response.json()

    got_from_MempoolSpace = False

    if (transactions):
        got_from_MempoolSpace = True
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Receive response OK')
        for i in range(len(transactions)):
            transactions[i]["feeRate"] = int_r(transactions[i]["fee"] / transactions[i]["vsize"])

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
    return got_from_MempoolSpace

def get_transactions():
    source = 'none'
    if get_transactions_from_MempoolSpace() == True:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] transactions were received')
        source = 'memepool.space'

    # else альтернативные источники

    return source



def get_mempool_from_file():
    with open('mempool.json', 'r') as f:
        mempool = json.load(f)
    return mempool


def count_stat():
    tr = get_mempool_from_file()
    for i in range(len(tr)):
        if tr[i]["feeRate"] == 1:
            fee_r[1] += 1

        if tr[i]["feeRate"] == 2:
            fee_r[2] += 1

        if tr[i]["feeRate"] == 3:
            fee_r[3] += 1

        if tr[i]["feeRate"] == 4:
            fee_r[4] += 1

        if tr[i]["feeRate"] == 5:
            fee_r[5] += 1

        if tr[i]["feeRate"] == 6:
            fee_r[6] += 1

        if tr[i]["feeRate"] == 7:
            fee_r[7] += 1

        if tr[i]["feeRate"] == 8:
            fee_r[8] += 1

        if tr[i]["feeRate"] == 9:
            fee_r[9] += 1

        if tr[i]["feeRate"] == 10:
            fee_r[10] += 1

        if tr[i]["feeRate"] == 11:
            fee_r[11] += 1

        if tr[i]["feeRate"] == 12:
            fee_r[12] += 1

        if tr[i]["feeRate"] == 13:
            fee_r[13] += 1

        if tr[i]["feeRate"] == 14:
            fee_r[14] += 1

        if tr[i]["feeRate"] == 15:
            fee_r[15] += 1

        if tr[i]["feeRate"] == 16:
            fee_r[16] += 1

        if tr[i]["feeRate"] == 17:
            fee_r[17] += 1

        if tr[i]["feeRate"] == 18:
            fee_r[18] += 1

        if tr[i]["feeRate"] == 19:
            fee_r[19] += 1

        if tr[i]["feeRate"] >= 20:
            fee_r['20&More'] += 1


def process(par):
    block_size = 1000000
    while True:
        if par.value == True:
            source = get_transactions()
            count_stat()
            feeRate_to_db()
            if sum_size() > block_size:
                if source == 'memepool.space':
                    compare_mempoolSpace()
            for key in fee_r:
                fee_r[key] = 0


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
    max_val = max(fee_r.values())
    final_dict = {k: v for k, v in fee_r.items() if v == max_val}
    avg = 0
    for d in final_dict.keys():
        avg = d
    if avg == '20&More':
        avg = 20
    return avg


def sum_size():  # вес всего мемпула
    with open('mempool.json', 'r') as f:
        Mempool = json.load(f)
        sum = 0
    for i in range(len(Mempool)):
        if Mempool[i]['vsize']:
            sum += Mempool[i]['vsize']
        else:
            sum += Mempool[i]['size']
    return sum


def amount_of_transactions():  # количество транзакций в пуле
    with open('mempool.json', 'r') as f:
        Mempool = json.load(f)
    count = 0
    for i in range(len(Mempool)):
        count += 1
    return count


def feeRate_to_db():
    avg = avg_feeRate()
    dt_now = datetime.now()
    t = dt_now.strftime("%Y-%m-%d-%H.%M.%S")
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS avgFee(Date , avg text);""")
    con.commit()
    cur.execute("""SELECT * FROM avgFee ORDER BY Date DESC LIMIT 1""")
    data = cur.fetchone()
    if (data is not None) and (data[1] == '20&More'):
        last = '20'
    if (data is not None) and (data[1] != '20&More'):
        last = data[1]
    if data is None:
        p = (t, avg)
        cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
        con.commit()
    elif (avg != int(last)):
        if avg == 20:
            avg = '20&More'
        p = (t, avg)
        cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
        con.commit()


def load_id(par):
    while True:
        if par.value == True:
            url = 'https://mempool.space/api/mempool/txids'
            response = requests.get(url)
            mempoolTxIds = response.json()
            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] get transactions IDs from mempool')
            with open('Mempool_id.json', 'w') as m:
                json.dump(mempoolTxIds, m, indent=4)
            response.close()
        time.sleep(60)


def compare_mempoolSpace():
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] deleting mined transactions')
    Mempool = []
    with open('Mempool_id.json', 'r') as f:
        mempoolTxIds = json.load(f)
    mempool = get_mempool_from_file()
    for i in range(len(mempool)):
        for j in range(len(mempoolTxIds)):
            if mempool[i]["txid"] == mempoolTxIds[j]:
                Mempool.append(mempool[i])
            else:
                if mempool[i]['feeRate'] == 1:
                    fee_r[1] -= 1

                if mempool[i]['feeRate'] == 2:
                    fee_r[2] -= 1

                if mempool[i]['feeRate'] == 3:
                    fee_r[3] -= 1

                if mempool[i]['feeRate'] == 4:
                    fee_r[4] -= 1

                if mempool[i]['feeRate'] == 5:
                    fee_r[5] -= 1

                if mempool[i]['feeRate'] == 6:
                    fee_r[6] -= 1

                if mempool[i]['feeRate'] == 7:
                    fee_r[7] -= 1

                if mempool[i]['feeRate'] == 8:
                    fee_r[8] -= 1

                if mempool[i]['feeRate'] == 9:
                    fee_r[9] -= 1

                if mempool[i]['feeRate'] == 10:
                    fee_r[10] -= 1

                if mempool[i]['feeRate'] == 11:
                    fee_r[11] -= 1

                if mempool[i]['feeRate'] == 12:
                    fee_r[12] -= 1

                if mempool[i]['feeRate'] == 13:
                    fee_r[13] -= 1

                if mempool[i]['feeRate'] == 14:
                    fee_r[14] -= 1

                if mempool[i]['feeRate'] == 15:
                    fee_r[15] -= 1

                if mempool[i]['feeRate'] == 16:
                    fee_r[16] -= 1

                if mempool[i]['feeRate'] == 17:
                    fee_r[17] -= 1

                if mempool[i]['feeRate'] == 18:
                    fee_r[18] -= 1

                if mempool[i]['feeRate'] == 19:
                    fee_r[19] -= 1

                if mempool[i]['feeRate'] == 20:
                    fee_r['20&More'] -= 1
    with open('mempool.json', 'w') as m:
        json.dump(Mempool, m, indent=4)
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] continue count')


def mine_block():
    Mempool = []
    with open('Mempool_id.json', 'r') as f:
        mempoolTxIds = json.load(f)
    mempool = get_mempool_from_file()
    for i in range(len(mempool)):
        for j in range(len(mempoolTxIds)):
            if mempool[i]["txid"] == mempoolTxIds[j]:
                Mempool.append(mempool[i])
    with open('mempool.json', 'w') as m:
        json.dump(Mempool, m, indent=4)
