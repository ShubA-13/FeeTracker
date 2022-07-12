import json
import requests
from datetime import datetime
import os
import sqlite3
import time

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

            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs ids cache size', len(transactions))
            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs cache size', sum_size())

        else:
            with open('mempool.json', 'r') as f:
                mempool = json.load(f)

            for i in range(len(transactions)):
                mempool.append(transactions[i])

            Mempool = check_same(mempool)

            with open('mempool.json', 'w') as m:
                json.dump(Mempool, m, indent=4)

            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs ids cache size', len(Mempool))
            print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] Mempool txs cache size', sum_size())


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
    if get_transactions_from_MempoolSpace() == True:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] transactions were received from mempool.space')


    elif get_transactions_from_BlockchainCom() == True:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] transactions were received from Blockchain.com')


def get_mempool_from_file():
    with open('mempool.json', 'r') as f:
        mempool = json.load(f)
    return mempool


def count_stat(tx):
    for i in range(len(tx)):
        if tx[i]['feeRate'] < 20:
            fr = int(tx[i]['feeRate'])
            fee_r[fr] += 1
        else:
            fee_r['20&More'] += 1

    print(fee_r)


def process(par):
    N = 1500000
    perv_block_size = 0
    now_block_size = 0
    while True:
        if par.value == True:
            get_transactions()
            txs = compare()
            now_block_size = amount_txs_mined(txs)
            if now_block_size == 0:
                mempool = get_mempool_from_file()
                count_stat(mempool)
                if amount_of_transactions() > 60:
                    feeR = avg_feeRate()
                    feeRate_to_db(feeR)
            elif now_block_size > perv_block_size:
                feeR = min_fee(txs)
                feeRate_to_db(feeR)
            else:
                mempool = get_mempool_from_file()
                count_stat(mempool)
                if amount_of_transactions() > 60:
                    feeR = avg_feeRate()
                    feeRate_to_db(feeR)
            perv_block_size = amount_txs_mined(txs)
            if sum_size_mined(txs) > N:
                new_block()
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
        fee_r_wo20 = fee_r.copy()
        fee_r_wo20.pop('20&More')
        max_val_wo20 = max(fee_r_wo20.values())
        final_dict_wo20 = {k: v for k, v in fee_r.items() if v == max_val_wo20}
        for i in final_dict_wo20.keys():
            avg_wo20 = i
        if fee_r['20&More'] / final_dict_wo20[avg_wo20] < 15:
            avg = avg_wo20

    if avg != '20&More':
        fee_r_m = fee_r.copy()
        fee_r_m.pop('20&More')
        fee_r_m.pop(avg)
        max_val_m = max(fee_r_m.values())
        final_dict_m = {k: v for k, v in fee_r_m.items() if v == max_val_m}
        for i in final_dict_m.keys():
            avg_m = i
        if avg_m > avg and fee_r[avg_m] / fee_r[avg] > 0.7:
            avg = avg_m

    if avg == '20&More':
        avg = 20
    if avg != '20&More':
        avg += 1
    print("mempool avg", avg)
    return avg


def sum_size_mined(txs):
    sum = 0
    for i in range(len(txs)):
        if txs[i]['source'] == 'mempool.space':
            sum += txs[i]['vsize']
        elif txs[i]['source'] == 'Blockchain.com':
            sum += txs[i]['size']
    return sum


def amount_txs_mined(txs):
    return len(txs)



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


def feeRate_to_db(feeR):
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
        p = (t, feeR)
        cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
        con.commit()
    elif (feeR != int(last)):
        if feeR == 20:
            feeR = '20&More'
        p = (t, feeR)
        cur.execute("INSERT INTO avgFee VALUES(?, ?);", p)
        con.commit()


def compare():
    mempool = get_mempool_from_file()
    Mempool = []
    block = []
    for i in range(len(mempool)):
        if mempool[i]['source'] == 'mempool.space':
            url = 'https://mempool.space/api/tx/'
            req = url + mempool[i]['txid'] + '/status'
            response = requests.get(req)
            info = response.json()
            isConfirmedMS = info['confirmed']
            if isConfirmedMS == True:
                block.append(mempool[i])
                if mempool[i]['feeRate'] < 20:
                    fr = mempool[i]['feeRate']
                    fee_r[fr] -= 1
                else:
                    fee_r['20&More'] -= 1
            else:
                Mempool.append(mempool[i])


        elif mempool[i]['source'] == 'Blockchain.com':
            url = 'https://blockchain.info/rawtx/'
            req = url + mempool[i]['txid']
            response = requests.get(req)
            info = response.json()
            isConfirmedB = info['block_index']
            if isConfirmedB == 'null':
                Mempool.append(mempool[i])
            else:
                block.append(mempool[i])
                if mempool[i]['feeRate'] < 20:
                    fr = mempool[i]['feeRate']
                    fee_r[fr] -= 1
                else:
                    fee_r['20&More'] -= 1

    with open('mempool.json', 'w') as m:
        json.dump(Mempool, m, indent=4)

    if os.stat('block.json').st_size == 0:
        with open('block.json', 'w') as m:
            json.dump(block, m, indent=4)

    else:
        with open('block.json', 'r') as f:
            block_txs = json.load(f)

        for i in range(len(block)):
            block_txs.append(block[i])

        with open('block.json', 'w') as m:
            json.dump(block, m, indent=4)

    print("block", block)
    print("mempool", Mempool)
    print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] continue count')
    return block

def clear_mempool():
    file = open('mempool.json', 'w')
    file.close()

def new_block():
    file = open('block.json', 'w')
    file.close()

def min_fee(txs):
    min = 1000000
    for i in range(len(txs)):
        if txs[i]['feeRate'] < min:
            min = txs[i]['feeRate']
    if min >= 20:
        min = '20&More'
    print('min in block', min)
    if min != '20&More':
        min += 1
    return min