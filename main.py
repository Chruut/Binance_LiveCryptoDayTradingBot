import json
import time
import websocket
import threading
import pandas as pd
from access import discord_token, discord_channel_id, api_key, api_secret 
#import re
from base_functions import *
from binance import Client
from binance.enums import *
from threading import Lock



def initialize_binance():
    try:
        client = Client(api_key, api_secret)
        return client
    except Exception as e:
        print(f"Fehler bei der Binance-Initialisierung: {e}")
        return None

def main():
    # Read in the Strategy Statistics Table provided by MetaSignals.io
    df = pd.read_excel('MetaTable.xlsx')
    
    # Initialize Binance client
    client = initialize_binance()
    if not client:
        print("Konnte keine Verbindung zu Binance herstellen. Programm wird beendet.")
        return


	
	# 1. Connect to Metasignals Discord Server
	dws = websocket.WebSocket()
	dws.connect('wss://gateway.discord.gg/?v=6&encording=json')
	event = recieve_json_response(dws)
	
	heartbeat_interval = event['d']['heartbeat_interval']/1000
	
	threading.Thread(target=heartbeat, args=(heartbeat_interval, dws)).start()
	send_json_request(dws,payload)
	
	deals_accepted = {} # This list should collect all the events which have lead to a deal and then a csv file is created in the end to save the financial progress. Ideally one would document directly how much money was made with each trade
	#open positions = {name of position A: Amount of cash, name of position B: Amount of cash}
	open_positions = {} # This logs the open positions and how much of the wallet is occupied
	signal_counter = 0
	closings = []
	print_lock = threading.Lock()
	position_lock = Lock()
	
	wallet_wealth = 100 #Total funds you want to play with

###################### MAIN PROGRAM LOOP ###############################
	while True:
	    
	    # 2. Start receiving Signals from Discord
	    event = recieve_json_response(dws)
	    try:
	        if event['op'] == 0 and event['t'] == 'MESSAGE_CREATE' and event['d']['channel_id'] == discord_channel_id:        # Check if the event is a MESSAGE_CREATE event and is from the target channel
	            # save the content in a dictionary
	            
	            #print(event['d']['content'])
	            essence = extraktion(event['d']['content'])
	            #print (essence)
	            
	            # The content of Discord scraper for example looks like this:    
	            # essence = {
	            #         "Position":position ,     #long or short
	            #         "Asset":asset ,           #BTC
	            #         "Currency":currency ,     #USDT
	            #         "Prize":prize ,           #0.359
	            #         "Candle":candle ,         #4H
	            #         "Strategy":strategy ,     #1.2
	            #         "T1":T1 ,                 #0.3713
	            #         "T2":T2 ,                 #0.3800
	            #         "T3":T3 ,                 #0.3924
	            #         "RR1":RR1 ,               #0.76
	            #         "RR2":RR2 ,               #1,33
	            #         "RR3":RR3 ,               #2.15
	            #         "Stop_loss":stop_loss     #0.3447    
	            #         }    
	    
	            # 3. CHECK WHETHER THERE IS ENOUGH SPACE FOR ANOTHER TRADING POSITION (<=12% OF WALLET)
	            try:
	                client = Client(api_key, api_secret)
	                account_data = client.get_account()
	                USDT_balance = float(client.get_asset_balance(asset='USDT')['free'])
	            except BinanceAPIException as e:
	                print(f"Binance API Fehler: {e}")
	            except Exception as e:
	                print(f"Unerwarteter Fehler: {e}")
			            
	            
	            percentage = sum_orders(open_positions)/USDT_balance
	            print(f"Currently, you have {len(open_positions)} open positions, totaling {percentage}% of your total balance.")
	            
	            if sum_orders(open_positions) > max_wallet_proportion * USDT_balance:
	                print("RESIST THE GREED! This signal has been avoided. Wallet too small! Insert more coins.")
	                continue
	            else:
	                print("Step 1. You still have funds to play! Order is being processed further")
	                
	                # STRATEGIZING
	                #check for strategy in excel file
	                strat = df[(df.Strategy == float(essence['Strategy'])) & (df.TF == essence['Candle'])]
	                
	                # at a later time when theres also short predictions: strat = df[(df.Strategy == essence['Strategy']) & (df.TF == essence['Candle']) & (df.Direction == essence['Position']) ]
	                
	                # 4. CHECK WHETHER THE STRATEGY IS IN METASIGNALS SELECTION OF VALID STRATEGIES. IF NOT SKIP THE SIGNAL
	                if strat.empty: # no strat with the given combinations
	                    print('No worthwhile Strategy found for the given Signal. I will skip this Signal.')
	                    continue
	                else: #continue                    
	                    tp_strat = strat.iloc[0]['TP'] #CHOICE OF TAKE PROFIT STRATEGY 
	                    # print(tp_strat)
	                    exit_price = essence[tp_strat] #CORRESPONDING TAKE PROFIT PRICE
	                    # print(exit_price)
	                    entry_price = essence['Stop_loss'] #ENTRY POINT AND STOP LOSS
	                    # print(entry_price)
	                    
	                    
	                    einsatz = stake_position * USDT_balance
	                    position = essence['Position']
	                    
	                    print(f'Step 2. Strategy {tp_strat} was chosen. Entry Price: {entry_price}, Take Profit: {exit_price}, Position: {position}, Einsatz: {einsatz} USD')
	                    
	                    
	                    #5. CREATE THE BINANCE MARKET ENTRY 
	                    signal_counter += 1
	                    
	                    sümbol = str(essence['Asset']+essence['Currency'])
	                    print(sümbol)
	                    # Find required Price Precision for the given asset
	                    info = client.futures_exchange_info(sümbol)
	                    print(info)
	                    # for symbol_info in info['symbols']:
	                    #     if symbol_info['symbol'] == sümbol:
	                    #         price_precision = symbol_info['pricePrecision']
	                    #         #flm_price = 
	                    #         print(f"The price precision for {sümbol} is {price_precision}.")
	                    #         break
	                    #     else:
	                    #         print(f"No information found for {sümbol}.")
	                    
	                    flm_quantity = round(einsatz / flm_price, price_precision) # final fund size that goes into the trade
	                    client.futures_change_leverage(symbol=sümbol, leverage=leverage) # set the leverage      
	  		    
			    # 6. TAKE FUTURES POSITION AND ENTER IT INTO BOOKKEEPING LISTS
	                    open_positions[signal_counter] = client.futures_create_order(symbol=sümbol, side='BUY', type = 'LIMIT', timeInForce='GTC', price=entry_price, quantity=flm_quantity)
	                    #['GTC', 'IOC', 'FOK', 'GTX', 'GTD']
	                    deals_accepted[signal_counter] = open_positions[signal_counter]
	                    prof = (exit_price - entry_price)*leverage # calculation of profit (Remark: need to subtract trading fees)
	
	                    print(open_positions[signal_counter])  
	                    
	                    
	                    #open_positions.append({"Name":connection.name,"Position":position, "Entry":entry_price, "Exit":exit_price, "Einsatz":einsatz})
	
			    # 7. OPEN A SHAKEOUT INSURANCE
	                    #Open a Binance API connection for Stop loss if closing below Stop_loss value
	                    candle = lower_except_M(essence['Candle'])
	                    #print(candle, type(candle))
	                    asset = (essence['Asset']+essence['Currency']).lower() + '@kline_' + candle
	                    
	                    connection = BinanceWebSocket(name=f"Connection-{signal_counter}", assets=asset, entry_price = entry_price, exit_price=exit_price,sümbol=sümbol) #A class which is defined in base_functions
	                    print(connection.name)
	                    
	                    threed = threading.Thread(target=connection.run_binance_websocket,name = f"Thread-{signal_counter}").start() # Open a new thread
	                
			    # FOLLOW THE COURSE AND IF STOP-LOSS SIGNAL IS TRIGGERED DONT CLOSE THE OPEN TRADE IMMEDIATELY, BUT RATHER WAIT FOR A PREDEFINED SHAKE OUT TIME AND IF THE SIGNAL IS THEN STILL OUTSIDE OF THE THRESHHOLD EXIT THE TRADE. 
	    except KeyError:
	        pass

if __name__ == "__main__":
    main()
