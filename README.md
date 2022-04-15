# FeeTracker
Transactions on the Bitcoin network require "fee", and the price of fee presents the demand for Bitcion blockspace at a given point in time.

The price of fee is extremely changeable, so it is preferably to make tranasactions when fee is cheap to save money, and also to avoid making
transactions when fee is expensive, unless it is really necessary.

This is a program designed to run as a background task. When it run, it gets transaction from now Bitcoin mempool and count optimal FeeRate presently,
FeeRate = fee/size sat/B. Then it stores the data to avgFee.db which created lockally and as well created json file with mempool lockally to check transactions'
feilds like "id", "size", "fee". 

To use this FeeTracker you need to clone this repository locally to your PC and build container by command `docker-compost up -d --build`
Then you can check optimal FeeRate in browser `http://localhost:5000/get_optional` and `http://localhost:5000/fee_in_period/from=<t1>&to=<t2>`, 
where **t1** and **t2** dates format [YYYY-MM-DD-HH-MM-SS], to get FeeRare in period from **t1** to **t2** (**t1** must be later).
