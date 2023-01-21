![Last commit](https://img.shields.io/github/last-commit/nelso0/BAS?style=plastic)
![Last commit](https://img.shields.io/github/languages/code-size/nelso0/BAS?style=plastic)
![Last commit](https://img.shields.io/github/directory-file-count/nelso0/BAS?style=plastic)
<p align="left">
  <img width="30%" height="30%" src="https://bas.teleporthq.app/playground_assets/bas-logo-rouge-600w.png">
</p>
 
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/nelsodot.svg?style=social&label=%20%40nelsodot)](https://twitter.com/nelsodot)
[![GitHub @nelso0](https://img.shields.io/github/followers/nelso0?label=follow&style=social)](https://github.com/nelso0)


More than a simple algorithm, [Barbotine Arbitrage System (B.A.S)](https://bas.teleporthq.app) is a complete portfolio management system based on the price difference opportunities of the same asset on several centralized trading platforms.
To eliminate the risks and variables to be taken into account, B.A.S operates without any transfer of assets between trading platforms. It also operates in a delta-neutral situation, which brings it even closer to zero risk.

## Features

* Complete trading fees support
* Can run on a demo without real money
* Delta-neutral mode
* Config file to edit every parameter
* Compatible with all [ccxt](https://github.com/ccxt/ccxt) exchanges simultaneously.

## Prerequisites

The things you need before installing the software.

* Python 3.*
* Machine which can run bash scripts (best is macOS or Linux env.)
* (not mandatory) AWS, Google Cloud or any cloud computing service to run the system 24/7
* [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) package installed

## Installation

1. Clone the repository 
```sh
$ git clone https://github.com/nelso0/BAS.git
```
2. Go to the B.A.S repository you just cloned
```sh
$ cd BAS
```
3. Install all the requirements to run the arbitrage system
```sh
$ pip install -r requirements.txt
```
4. Put your 3 api keys, passwords etc (binance, okx, kucoin) and your telegram bot details in [exchange_config.py](exchange_config.py)

**Then you're ready to run B.A.S!**

## Usage

Usage: 

```sh
$ bash main.sh [mode] [symbol-renew-time-minutes] [balance-usdt-to-use] {symbol}
```

* **[mode]** = the mode you wanna use among bot-fake-money, bot-classic, bot-delta-neutral. 
  
  * fake-money will run the bot with the balance-usdt-to-use you put, to test without any actual money.
  
  * classic will run the bot with actual money, for example if you put **1000**, you must have **333.3 USDT** in each of the 3 exchanges (don't worry it      won't run if you don't).
  
  * delta-neutral will do the same as bot-classic but will be delta-neutral by automatically placing a short order on kucoin-futures with the same size       of crypto that it'll buy for the arbitrage system. Therefore, you must have **333.33 USDT** in kucoin-futures account plus **666.66/3 = 222.22 USDT** in   each of the   three spot accounts (binance, kucoin, okx). You can put **0 USDT** in the kucoin-futures account and **222.22 + 333.33 USDT = 555.55 USDT**   in kucoin spot, it'll   transfer the needed amount to kucoin-futures.
  This mode can be useful if you don't renew the symbol often and you don't wanna be exposed to price change of the crypto over the time.

* **[symbol-renew-time-minutes]** = the timeframe you wanna use to switch symbol. If you put 60, it will renew the symbol each hour. Note that the new symbol is automatically selected by the [best_symbol.py](best-symbol.py) script.

* **[balance-usdt-to-use]** = how to be clearer? 

* **{symbol}** = Not mandatory. If you put a symbol, it will run continuously on this symbol, and so we don't care of [symbol-renew-time-minutes].

Examples

```sh
$ bash main.sh fake-money 15 1000    # run the system with 1000 USDT and renew symbol every 15 minutes.
```
```sh
$ bash main.sh classic 15 1000 SOL/USDT   # run the system with 1000 USDT on SOL/USDT continuously (change the symbol to SOL/USDT each 15 minutes).
```
```sh
$ bash main.sh delta-neutral 60 2000   # run the system in a delta-neutral situation with 2000 USDT and renew the symbol each hour. Note that with same amount of USDT, the delta-neutral mode will have 2/3 of the profits of the classic mode because it has less liquidity to invest in arbitrage opportunities. (Yes, a delta-neutral situation has a cost.)
```

## To do

- [x] Improve lisibility and UI
- [x] Add full trading fee support
- [ ] Improve the method to find the best symbol

## Contact

Twitter: [@nelsodot](https://twitter.com/nelsodo)

Discord: nelso#1800

Email: [nils.spen@gmail.com](mailto:nils.spen@gmail.com)

## License

In short: do what you want if it's personal-use, not commercial.
