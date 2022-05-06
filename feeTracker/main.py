from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
from multiprocessing import Process, Value
import funcs
import os

app = Flask(__name__)


@app.route('/get_optional', methods=['GET'])
def get_optional():
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    try:
        cur.execute("""SELECT * FROM avgFee ORDER BY Date DESC LIMIT 1""")
        data = cur.fetchone()
        response = {
            'date': data[0],
            'avg': data[1]
        }
        return jsonify(response), 200
    except:
        return jsonify('empty')


@app.route('/fee_in_period/', methods=['GET'])  # input date format YYYY-MM-DD-HH-MM-SS
def get_avg_in_period():
    t1 = request.args.get('to')
    t2 = request.args.get('from')
    if (t1 < t2):
        return jsonify('incorrect dates!')
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    try:
        sql_select_query = """SELECT * FROM avgFee """
        cur.execute(sql_select_query)
        recs = cur.fetchall()
        data = []
        for row in recs:
            if row[0] <= t1 and row[0] >= t2:
                data.append({'Data': row[0], 'avg': row[1]})
        if len(data) != 0:
            return jsonify(data), 200
        else:
            return jsonify('no results in this period')
    except:
        return jsonify('empty')


if __name__ == '__main__':

    # if not os.path.isfile('Mempool_id.json'):
    #     print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] lockal mempool is creating')
    #     file = open('Mempool_id.json', 'w')
    #     file.close()

    if not os.path.isfile('mempool.json'):
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] lockal list of mempool TXIDs is creating')
        file = open('mempool.json', 'w')
        file.close()

    if not os.path.isfile('avgFee.db'):
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] lockal DB is creating')
        file = open('avgFee.db', 'w')
        file.close()

    if os.stat('mempool.json').st_size != 0:
        print('[', datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), '] delete old transactions')
        funcs.compare()

    pars = Value('d', True)
    p = Process(target=funcs.process, args=(pars,))
    #d = Process(target=funcs.load_id, args=(pars,))
    #d.start()
    p.start()
    app.run(host='0.0.0.0', port=5000)
    #d.join()
    p.join()
