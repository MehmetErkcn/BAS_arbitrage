from asyncio import gather, run
import time
import random
import os
import requests
import ccxt.pro
import ccxt
import sys
from exchange_config import *
bid_prices = {}
ask_prices = {}
total_absolute_profit_pct=0
prec_ask_price = 0
prec_bid_price = 0
i=0
z=0
if len(sys.argv) != 5:
    print(f" \nUsage: $ python3 bot-classic.py [pair] [total_usdt_investment] [stop.delay.minutes] [tlgrm.msg.title]\n ")
    sys.exit(1)
print(" ")
for count in range(0,7):
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
avert = input("x"*140+str("\n \nIf all the x are not displayed on one line only, that means that your terminal window isn't large enough to display B.A.S correctly.\nPlease enlarge your terminal window to 140 characters per line min. if that is your case.\n \nType Enter to continue..."))
kucoinPair = str(sys.argv[1])
criteria_usd = str(criteria_usd)
criteria_pct = str(criteria_pct)
howmuchusd = float(sys.argv[2])
inputtimeout = int(sys.argv[3])*60
indicatif = str(sys.argv[4])
timeout = time.time() + inputtimeout

s=0

for n in echanges_str:
    bal = get_balance(n,"USDT")
    if float(bal) < float((howmuchusd)/len(echanges)):
        printandtelegram(f'Not enough balance on {n}. Need {round(float((howmuchusd)/len(echanges))-float(bal),3)} USDT more. Current balance on {n}: {round(bal,3)} USDT')
        s=1
if s==1:
    sys.exit(1)
usd = {exchange:(howmuchusd/2)/len(echanges) for exchange in echanges_str}
total_usd = usd['binance'] + usd['kucoin'] + usd['okx']

all_tickers = []

try:
    printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Fetching the global average price for {kucoinPair}...")
    for n in echanges:
        ticker = n.fetch_ticker(kucoinPair)
        all_tickers.append(ticker['bid'])
        all_tickers.append(ticker['ask'])
    average_first_buy_price = moy(all_tickers)
    total_crypto = (howmuchusd)/average_first_buy_price
    printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Average {kucoinPair} price in USDT: {average_first_buy_price}")

except Exception as e:
    print(f"Error while fetching average prices. Error: {e}")
    ex['binance'].close()
    ex['kucoin'].close()
    ex['okx'].close()

crypto = {exchange:total_crypto/len(echanges) for exchange in echanges_str}

crypto_per_transaction = total_crypto/len(echanges_str)

i=0
for n in echanges:
    n.createLimitBuyOrder(kucoinPair,total_crypto/len(echanges),average_first_buy_price)
    printandtelegram(f'[{time.strftime("%H:%M:%S", time.gmtime(time.time()))}] Buy limit order of {round(total_crypto/len(echanges),3)} {kucoinPair[:len(kucoinPair)-5]} at {average_first_buy_price} sent to {echanges_str[i]}.')
    i+=1

printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] All orders sent.")

timeout_first_buy = time.time()+5000

ordersFilled = 0
already_filled = []
while ordersFilled != 3:
    order1=ex['binance'].fetchOpenOrders(symbol=kucoinPair)
    if order1 == [] and already_filled.count("binance") == 0:
        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] binance order filled.")
        ordersFilled+=1
        already_filled.append("binance")
    order2=ex['kucoin'].fetchOpenOrders(symbol=kucoinPair)
    if order2 == [] and already_filled.count("kucoin") == 0:
        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] kucoin order filled.")
        ordersFilled+=1
        already_filled.append("kucoin")
    order3=ex['okx'].fetchOpenOrders(symbol=kucoinPair)
    if order3 == [] and already_filled.count("okx") == 0:
        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] okx order filled.")
        ordersFilled+=1
        already_filled.append("okx")
    time.sleep(2)

printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Starting program with parameters: {[n for n in sys.argv]}")
prec_time = '0000000'
min_ask_price = 0
async def symbol_loop(exchange, symbol):
    global crypto_per_transaction,i,z,prec_time,t,time1,bid_prices,ask_prices,total_absolute_profit_pct,min_ask_price,max_bid_price,prec_ask_price,prec_bid_price,timeout,profit_pct,profit_usd
    while time.time() <= timeout:
        try:
            orderbook = await exchange.watch_order_book(symbol)
            now = exchange.milliseconds()
            bid_prices[exchange.id] = orderbook["bids"][0][0]
            ask_prices[exchange.id] = orderbook["asks"][0][0]
            min_ask_ex = min(ask_prices, key=ask_prices.get)
            max_bid_ex = max(bid_prices, key=bid_prices.get)
            for u in echanges_str:
                if crypto[u] < crypto_per_transaction:
                    min_ask_ex = u
                if usd[u] <= 0: # should not happen
                    max_bid_ex = u
            min_ask_price = ask_prices[min_ask_ex]
            max_bid_price = ask_prices[max_bid_ex]
            best_diff = max_bid_price - min_ask_price
            best_diff_pct = ((max_bid_price - min_ask_price) / min_ask_price) * 100
            profit_usd = (min_ask_price*((total_crypto/len(echanges_str)))*((max_bid_price-min_ask_price)/min_ask_price))
            profit_pct = profit_usd/(0.01*total_usd)
            profit_with_fees_usd = profit_usd - (((crypto_per_transaction) * max_bid_price)*(fees[max_bid_ex]['receive']) + ((crypto_per_transaction * min_ask_price)*(fees[min_ask_ex]['give'])))
            profit_with_fees_pct = (profit_with_fees_usd/total_usd)*100
            
            if max_bid_ex != min_ask_ex and profit_with_fees_usd > float(criteria_usd) and profit_with_fees_pct > float(criteria_pct) and prec_ask_price != min_ask_price and prec_bid_price != max_bid_price and usd[min_ask_ex] >= crypto_per_transaction * min_ask_price * (1+fees[min_ask_ex]['give']):
                i+=1

                crypto[min_ask_ex] += crypto_per_transaction * (1-fees[min_ask_ex]['receive'])
                usd[min_ask_ex] -= crypto_per_transaction * min_ask_price * (1+fees[min_ask_ex]['give'])
                crypto[max_bid_ex] -= crypto_per_transaction * (1+fees[max_bid_ex]['give'])
                usd[max_bid_ex] += crypto_per_transaction * max_bid_price * (1+fees[max_bid_ex]['receive'])

                total_fees_crypto = crypto_per_transaction * (fees[max_bid_ex]['give']) + (crypto_per_transaction * (fees[min_ask_ex]['receive']))
                total_fees_usd = ((crypto_per_transaction) * max_bid_price)*(fees[max_bid_ex]['receive']) + ((crypto_per_transaction * min_ask_price)*(fees[min_ask_ex]['give']))

                total_absolute_profit_pct += profit_pct

                print(" ")
                print("-----------------------------------------------------")
                print(" ")
                printandtelegram(
                    f"[{indicatif} Trade n°{i}]\n \nOpportunity detected!\n \nProfit: {round(profit_pct,4)} % ({round(profit_usd,4)} USDT)\n \n{min_ask_ex} {min_ask_price}   ->   {max_bid_price} {max_bid_ex}\nTime elapsed: {time.strftime('%H:%M:%S', time.gmtime(time.time()-st))}\nTotal current profit: {round(total_absolute_profit_pct,4)} % ({round((total_absolute_profit_pct/100)*howmuchusd,4)} USDT)\nTotal fees paid: {total_fees_usd} USDT      {total_fees_crypto} {kucoinPair[:len(kucoinPair)-5]}\n \n--------BALANCES---------\n \nCurrent worth: {round((howmuchusd*(1+(total_absolute_profit_pct/100))),3)} USDT\n \n➝ binance: {round(crypto['binance'],3)} {kucoinPair[:len(kucoinPair)-5]} / {round(usd['binance'],2)} USDT\n➝ kucoin: {round(crypto['kucoin'],3)} {kucoinPair[:len(kucoinPair)-5]} / {round(usd['kucoin'],2)} USDT\n➝ okx: {round(crypto['okx'],3)} {kucoinPair[:len(kucoinPair)-5]} / {round(usd['okx'],2)} USDT\n \n"
                )

                ex[max_bid_ex].createLimitSellOrder(kucoinPair,crypto_per_transaction,max_bid_price)
                printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Sell limit order sent to {max_bid_ex} for {crypto_per_transaction} {kucoinPair[:len(kucoinPair)-5]} at {max_bid_price}, waiting 3 minutes for fill.")

                ex[min_ask_ex].createLimitBuyOrder(kucoinPair,crypto_per_transaction,min_ask_price)
                printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Buy limit order sent to {min_ask_ex} for {crypto_per_transaction} {kucoinPair[:len(kucoinPair)-5]} at {min_ask_price}, waiting 3 minutes for fill.")

                cancel_order_timeout = time.time() + 180
                already_filled = []
                while time.time()<cancel_order_timeout:
                    time.sleep(2)
                    buy_order = ex[min_ask_ex].fetchOpenOrders(symbol=kucoinPair)
                    sell_order = ex[max_bid_ex].fetchOpenOrders(symbol=kucoinPair)
                    if buy_order == [] and already_filled.count(min_ask_ex) == 0:
                        already_filled.append(min_ask_ex)
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {min_ask_ex} buy order filled!")
                    if sell_order == []and already_filled.count(max_bid_ex) == 0:
                        already_filled.append(max_bid_ex)
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {max_bid_ex} sell order filled!")
                    
                if buy_order != [] and sell_order == []:
                    printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {min_ask_ex} buy order is not filled in 3 minutes.")
                    try:
                        ex[min_ask_ex].cancelOrder(symbol=kucoinPair,id=buy_order[0]['id'])
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {min_ask_ex} buy order successfully cancelled.")
                    except Exception as e:
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Failed to cancel {min_ask_ex} buy order. Exit. Error: {e}")
                        sys.exit(1)
                    try:
                        last_opposite_orders = ex[max_bid_ex].fetchClosedOrders(kucoinPair)
                        ex[max_bid_ex].createMarketBuyOrder(kucoinPair,None,{"quoteOrderQty":float(last_opposite_orders[len(last_opposite_orders)-1]['cost'])})
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Reverse market order filled on {max_bid_ex}. Small losses to be taken into account.")
                    except Exception as e:
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Failed to create the reverse order on {max_bid_ex}. Exit. Error: {e}")
                        sys.exit(1)
                if sell_order != [] and buy_order == []:
                    printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {max_bid_ex} sell order is not filled in 3 minutes.")
                    try:
                        ex[max_bid_ex].cancelOrder(symbol=kucoinPair,id=sell_order[0]['id'])
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] {max_bid_ex} sell order successfully cancelled.")
                    except Exception as e:
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Failed to cancel {max_bid_ex} sell order. Exit. Error: {e}")
                        sys.exit(1)
                    try:
                        last_opposite_orders = ex[min_ask_ex].fetchClosedOrders(kucoinPair)
                        ex[min_ask_ex].createMarketSellOrder(symbol=kucoinPair,amount=float(last_opposite_orders[len(last_opposite_orders)-1]['filled']))
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Reverse market order filled on {min_ask_ex}. Small losses to be taken into account.")
                    except Exception as e:
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Failed to create the reverse order on {min_ask_ex}. Exit. Error: {e}")
                        sys.exit(1)
                if sell_order != [] and buy_order != []:
                    try:
                        printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] 2 orders not filled in 120 seconds. Cancel on his way.")
                        ex[min_ask_ex].cancelOrder(symbol=kucoinPair,id=buy_order[0]['id'])
                        ex[max_bid_ex].cancelOrder(symbol=kucoinPair,id=sell_order[0]['id'])
                    except Exception as e:
                        printandtelegram(f"A problem occured while trying to cancel the 2 orders. Exit. Error: {e}")
                        sys.exit(1)
            
                prec_ask_price = min_ask_price
                prec_bid_price = max_bid_price

                total_crypto = crypto["binance"]+crypto["kucoin"]+crypto["okx"]
                crypto_per_transaction = total_crypto/len(echanges_str)
            else:
                for count in range(0,1):
                    sys.stdout.write("\033[F")
                    sys.stdout.write("\033[K")
                print(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Best opportunity, profit in USD: {round(profit_with_fees_usd,4)} USD (with fees)       buy: {min_ask_ex} at {min_ask_price}     sell: {max_bid_ex} at {max_bid_price}       difference: {round(max_bid_price-min_ask_price,3)}")
            time1=exchange.iso8601(exchange.milliseconds())
            if time1[17:19] == "00" and time1[14:16] != prec_time:
                prec_time = time1[11:13]
                await exchange.close()
            z+=1

        except Exception as e:
            print(str(e))
            break  # you can break just this one loop if it fails

async def exchange_loop(exchange_id, symbols):
    exchange = getattr(ccxt.pro, exchange_id)()
    loops = [symbol_loop(exchange, symbol) for symbol in symbols]
    await gather(*loops)
    await exchange.close()

async def main():
    exchanges = {
        "kucoin": [kucoinPair],
        "binance": [kucoinPair],
        "okx":[kucoinPair]
    }
    loops = [
        exchange_loop(exchange_id, symbols)
        for exchange_id, symbols in exchanges.items()
    ]
    await gather(*loops)

st = time.time()
print(" \n")
run(main())

with open('balance.txt', 'r+') as balance_file:
    balance = float(balance_file.read())
    balance_file.seek(0)
    balance_file.write(str(round(balance * (1 + (total_absolute_profit_pct/100)), 3)))
    balance = float(round(balance * (1 + (total_absolute_profit_pct/100)), 3))

printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Selling all {sys.argv[1][:len(sys.argv[1])-5]} on {echanges_str}.")
emergency_convert(str(kucoinPair))

printandtelegram(f"[{time.strftime('%H:%M:%S', time.gmtime(time.time()))}] Session with {kucoinPair} finished.\nTotal profit: {round(total_absolute_profit_pct,4)} % ({round((total_absolute_profit_pct/100)*howmuchusd,4)}) USDT\n \nTotal current balance: {balance} USDT")