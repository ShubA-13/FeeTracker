import json
import requests
import datetime
from pprint import pprint
import os

url = 'https://mempool.space/api/mempool/recent'
response = requests.get(url)
transactions = response.json()



for i in range(len(transactions)):
    for k in range(len(transactions)):
        now = datetime.datetime.today()
        transactions[k]["date"] = now.strftime("%Y-%m-%d-%H.%M.%S")

        transactions[k]["feeRate"] = transactions[k]["fee"] / transactions[i]["vsize"]
    for j in range(0, len(transactions) - i - 1):
        if (transactions[j]["feeRate"] < transactions[j + 1]["feeRate"]):
            a = transactions[j]
            transactions[j] = transactions[j + 1]
            transactions[j + 1] = a


if os.stat('mempool1.json').st_size == 0:
    with open('mempool1.json', 'w') as m:
        json.dump(transactions, m, indent = 4)
else:
    with open('mempool2.json', 'w') as m:
        json.dump(transactions, m, indent = 4)


with open('mempool1.json', 'r') as f:
    mempool1 = json.load(f)


if os.stat('mempool2.json').st_size != 0:
    with open('mempool2.json', 'r') as f:
        mempool2 = json.load(f)

    for i in range(len(mempool2)):
        mempool1.append(mempool2[i])

    count = 0
    for i in range(len(mempool1)):
        for j in range(0, len(mempool1) - i - 1):
            if mempool1[j]['feeRate'] < mempool1[j+1]['feeRate']:
                a = mempool1[j]
                mempool1[j] = mempool1[j+1]
                mempool1[j+1] = a

pprint(mempool1)

maxFeeRate = 0
for i in range(len(mempool1)):
    if mempool1[i]['feeRate'] > maxFeeRate:
        maxFeeRate = mempool1[i]['feeRate']

print(f"Max fee rate: {maxFeeRate} sat/vB")

count = 0
oneBlockSize = 1000000
sum = 0
s = 0
nearBlockMinFee_number = 0
for i in range(len(mempool1)):
    count += 1
    s += mempool1[i]['vsize']
#     sum += mempool1[i]['vsize']
#     while sum <= oneBlockSize:
#         nearBlockMinFee_number = i
#
#last = mempool1[nearBlockMinFee_number]['feeRate'] #fee последней транзакции, котроая войдет в блок
# print(f"Нижняя граница попадания транзакции в блок {mempool1[nearBlockMinFee_number]['feeRate']}")
print("Количество транзакций в пуле: ", count)
print("size: ", s)
# for i in range(nearBlockMinFee_number):
#     sum += mempool1[i]['feeRate']
#
# avg_feeRate = sum / nearBlockMinFee_number
# print(f"Среднее FeeRate: {avg_feeRate} sat/vB")


with open('mempool1.json', 'w') as m:
    json.dump(mempool1, m, indent=4)

















