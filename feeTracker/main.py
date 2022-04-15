from flask import Flask, jsonify, request
import sqlite3
import time
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
    t1 = request.args.get('from')
    t2 = request.args.get('to')
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


def adding(par):
    while True:
        if par.value == True:
            funcs.feeRate_to_db()
        time.sleep(60)


if __name__ == '__main__':
    if not os.path.isfile('Mempool_id.json'):
        file = open('Mempool_id.json', 'w')
        file.close()

    if not os.path.isfile('mempool.json'):
        file = open('mempool.json', 'w')
        file.close()

    if not os.path.isfile('avgFee.db'):
        file = open('avgFee.db', 'w')
        file.close()

    if os.stat('mempool.json').st_size != 0:
        funcs.mempool()
    pars = Value('d', True)
    p = Process(target=adding, args=(pars,))
    d = Process(target=funcs.load_id, args=(pars,))
    d.start()
    p.start()
    app.run(host='0.0.0.0', port=5000)
    d.join()
    p.join()
