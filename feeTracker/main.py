from flask import Flask, jsonify
import sqlite3
import time
from multiprocessing import Process, Value
import funcs

app = Flask(__name__)


@app.route('/get_optional', methods=['GET'])
def get_optional():
    con = sqlite3.connect('avgFee.db')
    cur = con.cursor()
    cur.execute("""SELECT * FROM avgFee ORDER BY Date DESC LIMIT 1""")
    try:
        data = cur.fetchone()
        response = {
            'date': data[0],
            'avg': data[1]
        }
        return jsonify(response), 200
    except:
        return jsonify("error: empty")

@app.route('/fee_in_period/from=<t1>&to=<t2>', methods=['GET']) #input date format YYYY-MM-DD-HH-MM-SS
def get_avg_in_period(t1, t2):

    con = sqlite3.connect('avgFee.db') # 2022-03-27-14.11.21
    cur = con.cursor() # 2022-03-22-22.19.00
    sql_select_query = """SELECT * FROM avgFee """
    cur.execute(sql_select_query)
    recs = cur.fetchall()
    data = []
    for row in recs:
        if row[0] <= t1 and row[0] >= t2:
            data.append({'Data': row[0], 'avg': row[1]})
    return jsonify(data), 200


def adding(par):

        while True:
            if par.value == True:
                funcs.feeRate_to_db()
            time.sleep(60)



if __name__ == '__main__':
    pars = Value('d', True)
    p = Process(target=adding, args=(pars,))
    p.start()
    app.run(host='0.0.0.0', port=5000)
    p.join()
