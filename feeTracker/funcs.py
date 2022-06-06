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
            transactions[i]['source'] = 'mempool.space'

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


def get_transactions_from_BlockchainCom():
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"),
          '] Send request https://blockchain.info/unconfirmed-transactions?format=json')
    url = 'https://blockchain.info/unconfirmed-transactions?format=json'
    response = requests.get(url)
    transactions = response.json()

    got_from_BlocchainCom = False

    if (transactions):
        mempool_reform = []
        got_from_BlocchainCom = True
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Receive response OK')
        tr_vals = transactions['txs']
        # print(tr_vals)
        for i in range(len(tr_vals)):
            mempool_reform.append({'txid': tr_vals[i]['hash'], 'fee': tr_vals[i]['fee'], 'size': tr_vals[i]['size'],
                                   'feeRate': int_r(tr_vals[i]['fee'] / tr_vals[i]['size']),
                                   'source': 'Blockchain.com'})
        print(mempool_reform)

        if os.stat('mempool.json').st_size == 0:
            with open('mempool.json', 'w') as m:
                json.dump(mempool_reform, m, indent=4)

        else:
            with open('mempool.json', 'r') as f:
                mempool = json.load(f)

            for i in range(len(mempool_reform)):
                mempool.append(mempool_reform[i])

            Mempool = check_same(mempool)

            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs ids cache size', len(Mempool))
            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs cache size', sum_size())

            with open('mempool.json', 'w') as m:
                json.dump(Mempool, m, indent=4)

    else:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Receive error response with 404')

    response.close()
    return got_from_BlocchainCom


def get_transactions():
    # source = 'none'
    if get_transactions_from_MempoolSpace() == True:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] transactions were received from mempool.space')
        # source = 'memepool.space'

    elif get_transactions_from_BlockchainCom() == True:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] transactions were received from Blockchain.com')
        # source = 'Blockchain.com'

    # return source


def get_mempool_from_file():
    with open('mempool.json', 'r') as f:
        mempool = json.load(f)
    return mempool


def count_stat():
    tr = get_mempool_from_file()
    for i in range(len(tr)):
        if tr[i]['feeRate'] < 20:
            fr = int(tr[i]['feeRate'])
            fee_r[fr] += 1
        else:
            fee_r['20&More'] += 1

    print(fee_r)


def process(par):
    block_size = 1000000
    while True:
        if par.value == True:
            get_transactions()
            count_stat()
            feeRate_to_db()
            if sum_size() > block_size:
                # if source == 'memepool.space':
                #     compare_mempoolSpace()
                # if source == 'Blockchain.com':
                #     compare_mempoolSpace()
                compare()
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
    Mempool = get_mempool_from_file()
    sum = 0
    for i in range(len(Mempool)):
        if Mempool[i]['source'] == 'mempool.space':
            sum += Mempool[i]['vsize']
        elif Mempool[i]['source'] == 'Blockchain.com':
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


# def load_id(par):
#     while True:
#         if par.value == True:
#             url = 'https://mempool.space/api/mempool/txids'
#             response = requests.get(url)
#             mempoolTxIds = response.json()
#             print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] get transactions IDs from mempool')
#             with open('Mempool_id.json', 'w') as m:
#                 json.dump(mempoolTxIds, m, indent=4)
#             response.close()
#         time.sleep(30)


def compare():
    mempool = get_mempool_from_file()
    Mempool = []
    for i in range(len(mempool)):
        if mempool[i]['source'] == 'mempool.sapce':
            url = 'https://mempool.space/api/tx/'
            req = url + mempool[i]['txid']
            response = requests.get(req)
            info = response.json()
            isConfirmedMS = info['status']['confirmed']
            if isConfirmedMS != 'True':
                Mempool.append(mempool[i])
            else:
                if mempool[i]['feeRate'] < 20:
                    fr = mempool[i]['feeRate']
                    fee_r[fr] -= 1
                else:
                    fee_r['20&More'] -= 1

        elif mempool[i]['source'] == 'Blockchain.com':
            url = 'https://blockchain.info/rawtx/'
            req = url + mempool[i]['txid']
            response = requests.get(req)
            info = response.json()
            isConfirmedB = info['block_index']
            if isConfirmedB == 'null':
                Mempool.append(mempool[i])
            else:
                if mempool[i]['feeRate'] < 20:
                    fr = mempool[i]['feeRate']
                    fee_r[fr] -= 1
                else:
                    fee_r['20&More'] -= 1

    with open('mempool.json', 'w') as m:
        json.dump(Mempool, m, indent=4)
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] continue count')

# def mine_block():
#     Mempool = []
#     with open('Mempool_id.json', 'r') as f:
#         mempoolTxIds = json.load(f)
#     mempool = get_mempool_from_file()
#     for i in range(len(mempool)):
#         for j in range(len(mempoolTxIds)):
#             if mempool[i]["txid"] == mempoolTxIds[j]:
#                 Mempool.append(mempool[i])
#     with open('mempool.json', 'w') as m:
#         json.dump(Mempool, m, indent=4)
