import numpy as np
import time
from datetime import datetime, timezone, timedelta
import requests
import hmac
import hashlib
import yaml
import json


# Binance Rest API documentation
# https://github.com/binance-us/binance-official-api-docs/blob/master/rest-api.md
# Each url gets you slightly different information and has slightly different input params
# api/v3/exchangeInfo, api/v3/depth, api/v3/trades, etc...

# Disclaimer:
# I do not provide personal investment advice and I am not a qualified licensed investment advisor. 
# The information provided may include errors or inaccuracies. Conduct your own due diligence, or consult
# a licensed financial advisor or broker before making any and all investment decisions. Any investments, 
# trades, speculations, or decisions made on the basis of any information found on this site and/or script, 
# expressed or implied herein, are committed at your own risk, financial or otherwise. No representations 
# or warranties are made with respect to the accuracy or completeness of the content of this entire site 
# and/or script, including any links to other sites and/or scripts. The content of this site and/or script
# is for informational purposes only and is of general nature. You bear all risks associated with the use 
# of the site and/or script and content, including without limitation, any reliance on the accuracy, 
# completeness or usefulness of any content available on the site and/or script. Use at your own risk.


config = yaml.safe_load(open('config.yml')) # Load yaml file that has api and secret key

apikey=config['apikey'] # Api key from yaml file
secretkey=config['secretkey'] # Secret key from yaml file

symbol_pair='BNBBUSD' # Pair to trade
symbol_first='BNB' # Make sure this matches above
symbol_second='BUSD' # Make sure this matches above

def current_price():

    #################################
    ##### Ticker price endpoint ##### 
    #################################
    urlcp='https://api.binance.us/api/v3/ticker/price'

    
    paramscp={'symbol':symbol_pair} # Ticker wanted
    response_cp = requests.get(urlcp, params=paramscp) # Sending GET request for ticker information
    # print(response_cp) # Returns HTTP Status, a value of 200 (OK) means no error

    pair_info = response_cp.json() # Convert response to JSON object for data extraction
    # print(json.dumps(pair_info, indent=4)) # Pretty print to understand structure of data
    cp = pair_info['price'] # Current price of symbol

    
    print('--------------------Current Price--------------------')
    print(f'{symbol_pair} Current Price: {cp}')
    print('\n')

    return cp


def account_balance():

    print('###############################################################')
    print('########################Account Balance########################')
    print('###############################################################')
    print('\n\n')

    ########################################
    ##### Account information endpoint ##### 
    ########################################
    url = "https://api.binance.us/api/v3/account" 


    # Creating datetime variable required for account connection
    now = datetime.now(timezone.utc) # current date
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)  # use POSIX epoch
    posix_timestamp_micros = (now - epoch) // timedelta(microseconds=1)
    posix_timestamp_millis = posix_timestamp_micros // 1000  # or `/ 1e3` for float

    # Input variables
    queryString = "timestamp=" + str(posix_timestamp_millis) 
    # Creating hash for authentication
    signature = hmac.new(secretkey.encode(), queryString.encode(), hashlib.sha256).hexdigest() 
    # Combining account information endpoint url with input variables and authentication hash
    url = url + f"?{queryString}&signature={signature}"

    # Sending GET request for account information
    response_ai = requests.get(url, headers={'X-MBX-APIKEY': apikey})

    # Convert response to JSON object for data extraction
    account_info=response_ai.json()
    # print(json.dumps(account_info, indent=4)) # Pretty print to understand structure of data


    # Can't call out the symbols directly because 'balances' is a list of dictionaries and not a dictionary
    # Cycle through the list of dictionaries containing the different assets
    for i, balance in enumerate(account_info['balances']):

        if balance['asset']==symbol_first: # Finding first symbol in symbol pair
            ifirst=i

        if balance['asset']==symbol_second: # Finding second symbol in symbol pair
            isecond=i

    # First asset information
    asset=account_info['balances'][ifirst]['asset'] # Asset name
    assetfree=account_info['balances'][ifirst]['free'] # Asset amount that is free to trade
    assetlocked=account_info['balances'][ifirst]['locked'] # Asset amount that is locked and can't be traded
    
    assetfreecp=float(assetfree)*float(cp) # Current price of asset that is free
    assetlockedcp=float(assetlocked)*float(cp) # Current price of asset that is locked

    # Printing information
    print(f'Asset: {asset}')
    print(f'Free: {assetfree} at {cp} = ${assetfreecp}' )
    print(f'Locked: {assetlocked} at {cp} = ${assetlockedcp}')
    print(f'Subtotal: $ {assetfreecp+assetlockedcp}')
    print(f'Subtotal: $ {assetfreecp+assetlockedcp}')
    print('\n')

    print('+')
    print('\n')

    # Second asset information
    asset2=account_info['balances'][isecond]['asset'] # Asset name
    assetfree2=account_info['balances'][isecond]['free'] # Asset amount that is free to trade
    assetlocked2=account_info['balances'][isecond]['locked'] # Asset amount that is locked and can't be traded

    # Printing information
    print(f'Asset: {asset2}')
    print(f'Free: {assetfree2}')
    print(f'Locked: {assetlocked2}')
    print(f'Subtotal: {float(assetfree2)+float(assetlocked2)}')
    print('\n')

    # Total net worth in account
    print('----------Total----------')
    print('$',assetfreecp+assetlockedcp+float(assetfree2)+float(assetlocked2))
    print('\n\n')

    print('###############################################################')
    print('########################Account Balance########################')
    print('###############################################################')
    print('\n')

    return assetfree, assetfree2


def latest_transaction():

    ###################################
    ##### Account trades endpoint ##### 
    ###################################
    url = "https://api.binance.us/api/v3/myTrades"


    # Creating datetime variable required for account connection
    now = datetime.now(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)  # use POSIX epoch
    posix_timestamp_micros = (now - epoch) // timedelta(microseconds=1)
    posix_timestamp_millis = posix_timestamp_micros // 1000  # or `/ 1e3` for float

    # Input variables
    queryString = "symbol=" + symbol_pair + "&timestamp=" + str(posix_timestamp_millis)
    # Creating hash for authentication
    signature = hmac.new(secretkey.encode(), queryString.encode(), hashlib.sha256).hexdigest()
    # Combining account information endpoint url with input variables and authentication hash
    url = url + f"?{queryString}&signature={signature}"

    # Sending GET request for account trades
    response_trades = requests.get(url, headers={'X-MBX-APIKEY': apikey})

    # Convert response to JSON object for data extraction
    trades=response_trades.json()
    # print(json.dumps(trades, indent=4)) # Pretty print to understand structure of data

    latest_transaction=trades[-1] # Latest transaction

    print('--------------------Latest Transaction--------------------')
    print('\n')

    tp=latest_transaction['symbol'] # Trading pair
    tp_price=latest_transaction['price'] # Trading pair price

    # Printing information
    print(f'Trading Pair: {tp}')
    print(f'Price: {tp_price}')
    print('\n')

    # Buy and Sell is for the first symbol of the trading pair
    # True is buy first symbol
    # False is sell first symbol
    isBuyer= latest_transaction['isBuyer']

    symbol_first_qty = latest_transaction['qty'] # First Symbol quantity
    symbol_second_qty = latest_transaction['quoteQty'] # Second Symbol quantity

    # Buy first symbol
    if isBuyer == True:

        print('BUY')
        print(f'{symbol_first} BOUGHT:  {symbol_first_qty}')
        print(f'{symbol_second} SOLD: {symbol_second_qty}')

    # Sell first symbol
    elif isBuyer == False:

        print('SELL')
        print(f'{symbol_first} SOLD:  {symbol_first_qty}')
        print(f'{symbol_second} BOUGHT: {symbol_second_qty}')
    print('\n')

    return tp_price, isBuyer


def submit_order():

    ##########################
    ##### Order endpoint ##### 
    ##########################
    url = "https://api.binance.us/api/v3/order"
    # url = "https://api.binance.us/api/v3/order/test" # Test url for dummy trades

    # Creating datetime variable required for account connection
    now = datetime.now(timezone.utc)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)  # use POSIX epoch
    posix_timestamp_micros = (now - epoch) // timedelta(microseconds=1)
    posix_timestamp_millis = posix_timestamp_micros // 1000  # or `/ 1e3` for float

    # Input variables
    type='MARKET' # Order type

    if isBuyer == False:
        side='BUY' # Want to buy
        quoteOrderQty=str(symbol_second_avail) # How much second symbol you want to use to buy first symbol
        queryString = "symbol=" + symbol_pair + "&side=" + side + "&type=" + type + "&quoteOrderQty=" + quoteOrderQty +  "&timestamp=" + str(posix_timestamp_millis)
    
    elif isBuyer == True:
        side='SELL' # Want to sell
        quantity=str(symbol_first_avail) #how much first symbol you want to sell to buy second symbol
        queryString = "symbol=" + symbol_pair + "&side=" + side + "&type=" + type + "&quantity=" + quantity +  "&timestamp=" + str(posix_timestamp_millis)

    # Creating hash for authentication
    signature = hmac.new(secretkey.encode(), queryString.encode(), hashlib.sha256).hexdigest()
    # Combining account information endpoint url with input variables and authentication hash
    url = url + f"?{queryString}&signature={signature}"

    # Sending POST request for order
    response_order = requests.post(url, headers={'X-MBX-APIKEY': apikey})

    # Convert response to JSON object for data extraction
    order=response_order.json()
    # print(json.dumps(order, indent=4)) # Pretty print to understand structure of data

    symbol_first_transaction=order['executedQty'] # How much of first symbol was bought/sold
    symbol_second_transaction=order['cummulativeQuoteQty'] # How much of second symbol was sold/bought
    fills=order['fills'] # Order fill information

    # Printing information

    if isBuyer == False:

        print('########################BOUGHT!########################')
        print(f'{symbol_first} Bought: {symbol_first_transaction}')
        print(f'{symbol_second} Sold: {symbol_second_transaction}')
        print(f'Fills: {fills}')
        print('########################BOUGHT!########################')

    elif isBuyer == True:

        print('########################SOLD!########################')
        print(f'{symbol_first} Sold: {symbol_first_transaction}')
        print(f'{symbol_second} Bought: {symbol_second_transaction}')
        print(f'Fills: {fills}')
        print('########################SOLD!########################')

    print('\n\n')

    time.sleep(5) # In seconds





while True: # Continuously Run

    print('--------------------------------------------------New Check-------------------------------------------------')
    print('----------------------------------------',datetime.now(),'----------------------------------------')
    print('\n')

    #################
    # Current Price #
    #################

    cp = current_price() # Current price of symbol


    ###################
    # Account Balance #
    ###################

    assetfree, assetfree2 = account_balance()

    time.sleep(5)


    ######################
    # Latest Transaction #
    ######################

    tp_price, isBuyer = latest_transaction()


    #####################
    # BUY/SELL Criteria #
    #####################

    print('--------------------BUY/SELL Criteria--------------------')
    print('\n')

    # Trading fee is .075% if using bnb for fees https://www.binance.com/en/fee/schedule
    # Buy Sell Percentage bsp below must be greater than trading fee
    # But also needs to include a bit more margin to account for slippage since this script does market orders
    bsp=0.5 #buy/sell percent criteria in %
    print('Buy/Sell Percent Criteria: ', bsp, '%')
    delta=bsp/100*float(tp_price) # Delta of price calculated from buy/sell percent criteria 
    print('Buy/Sell Criteria Delta (Previous Price * Percent): $', delta)
    print('\n')

    #################
    # Current Price #
    #################

    # Do this again to get the latest and greatest price since prices change so quickly
    cp = current_price() # Current price of symbol


    ##################
    ##### Buying #####
    ##################

    if  isBuyer == False: # If latest transaction was a SELL

        buyprice=float(tp_price) - delta # Price to buy at
        print('--------------------Checking to see if time to BUY--------------------')
        print(f'Needed Price to Buy (Previous Price - Delta): ${buyprice}')
        print('\n')

        ###################
        ##### Yes Buy #####
        ###################

        if float(cp) < buyprice:

            print('YES!')
            print(f'Current Price: {cp} < BUY Price: {buyprice}')
            print('\n')

            symbol_second_avail=np.floor(float(assetfree2)) # Round down to nearest whole number for second asset
            print(f'{symbol_second} Available: {symbol_second_avail}')
            print('\n')

            ################
            # Submit Order #
            ################

            # submit_order()

            ###################
            # Account Balance #
            ###################

            #Do this again to get the latest and greatest account info after the new trade
            assetfree, assetfree2 = account_balance()


        ##################
        ##### No Buy #####
        ##################

        elif float(cp) > buyprice:

            print('NO! PRICE IS HIGH!')
            print(f'Current Price: {cp} > BUY Price: {buyprice}')


        ##################
        ##### No Buy #####
        ##################

        elif float(cp) == buyprice:

            print('NO! PRICE IS SAME!')
            print(f'Current Price: {cp} = BUY Price: {buyprice}')


    ###################
    ##### Selling #####
    ###################

    elif isBuyer == True: # If latest transaction was a BUY

        sellprice=float(tp_price) + delta # Price to sell at
        print('--------------------Checking to see if time to SELL--------------------')
        print(f'Needed Price to Sell (Previous Price + Delta): ${sellprice}')
        print('\n')

        ####################
        ##### Yes Sell #####
        ####################

        if float(cp) > sellprice:

            print('YES!')
            print(f'Current Price: {cp} > SELL Price: {sellprice}')

            # Round down to nearest hundredths place 0.01 for first asset
            n_decimals=2
            a=float(assetfree)
            symbol_first_avail=((a*10**n_decimals)//1)/(10**n_decimals)
            print(f'{symbol_first} Available: {symbol_first_avail}')

            ################
            # Submit Order #
            ################

            # submit_order()

            ###################
            # Account Balance #
            ###################

            #Do this again to get the latest and greatest account info after the new trade
            assetfree, assetfree2 = account_balance()


        ###################
        ##### No Sell #####
        ###################

        elif float(cp) < sellprice:

            print('NO! PRICE IS LOW!')
            print(f'Current Price: {cp} < SELL Price: {sellprice}')


        ###################
        ##### No Sell #####
        ###################
        
        elif float(cp) == sellprice:

            print('NO! PRICE IS SAME!')
            print(f'Current Price: {cp} = SELL Price: {sellprice}')


    print('\n\n\n\n')
    time.sleep(60*60) # In seconds