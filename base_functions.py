import json
import time
import re
import websocket
import pandas as pd
from datetime import timedelta
from binance import Client
from binance.enums import *
    


# TRADING BOT PARAMETERS
max_wallet_proportion = 0.12 #maximal proportion of crypto wallet you allow to be in play
stake_position = 0.02 #stake per game (accepted signal) as percentage of total usdt balance
leverage = 2 #leverage per game
order_patience_time = 3000



# Discord Part
def send_json_request(dws, request):
	dws.send(json.dumps(request))



def recieve_json_response(dws):
	response = dws.recv()
	if response:
		return json.loads(response)

def heartbeat(interval, dws):
	print("Heartbeat begin")
	
	while True:
		time.sleep(interval)
		heartbeatJSON = {
			"op": 1,
			"d": "null"

		}

		send_json_request(dws, heartbeatJSON)
		print("Heartbeat sent")

# def on_message(ws, message):
#     message = json.loads(message)
#     print(message['data']['k']['x'])
  
def extraktion(gulasch):
    text = gulasch
    #print(text)
    lines = text.splitlines()
    elements = lines[0].split()



    #POSITION
    pos = elements[0]
    pattern = re.compile(r'([\U0001F4C8]+)')

    # Use findall to find all matches in the text
    matches = pattern.findall(pos)

    # Check if there are any matches
    if matches:
        position = "long"
    else:
        position = "short"

    #REST OF FIRST LINE
    asset = elements[1]
    currency = elements[3]
    prize = elements[5]
    prize = prize[1:]
    candle = elements[7]
    strategy = elements[10]
    #print(position, asset, currency, prize, candle, strategy)

    #TARGETS
    target1 = re.split(pattern = r" |\)",
                       string = lines[2])
    #print(target1)
    T1 = target1[2]
    RR1 = target1[4]

    target2 = re.split(pattern = r" |\)",
                       string = lines[3])
    T2 = target2[2]
    RR2 = target2[4]

    target3 = re.split(pattern = r" |\)",
                       string = lines[4])
    T3 = target3[2]
    RR3 = target3[4]

    #print(T1,T2,T3,RR1,RR2,RR3)

    stop_loss = lines[5].split()[3]
    #print(stop_loss)
    #print(position, asset, currency, prize, candle, strategy, T1,T2,T3,RR1,RR2,RR3,stop_loss)
    global essence
    essence = {
        "Position":position ,
        "Asset":asset ,
        "Currency":currency ,
        "Prize":float(prize) ,
        "Candle":candle ,
        "Strategy":strategy ,
        "TP1":float(T1) ,
        "TP2":float(T2) ,
        "TP3":float(T3) ,
        "RR1":float(RR1) ,
        "RR2":float(RR2) ,
        "RR3":float(RR3) ,
        "Stop_loss":float(stop_loss)              
        }

    for key, value in essence.items():
        print(f"{key}: {value}")
    return essence


def sum_orders(dictionary_list):
    total = 0

    for diction in dictionary_list:
        if 'Einsatz' in diction:
            total += diction['Einsatz']

    return total

def lower_except_M(input_string):
    result = ''
    
    for char in input_string:
        if char.isalpha() and char.lower() != 'm':
            result += char.lower()
        else:
            result += char

    return result


class BinanceWebSocket:
    def __init__(self, name, assets, entry_price, exit_price, sümbol):
        self.name = name
        self.assets = assets
        self.sümbol = sümbol
        self.k_close = False # needed?
        self.k_mark = 0 # needed?
        self.source = None # needed?
        self.exit_price = exit_price
        self.entry_price = entry_price
        self.socket = f"wss://stream.binance.com:9443/stream?streams={self.assets}"
        self.ws = websocket.WebSocketApp(self.socket, on_message=self.on_message)

    def manipulation (self, source):
        rel_data = source['data']['k']['c']
        event_time = pd.to_datetime(source ['data']['E'], unit= 'ms')
        doof = pd.DataFrame(rel_data, columns = [source['data']['s']],
                            index = [event_time])
        
        doof.index.name = 'timestamp'
        doof = doof.astype(float)
        doof = doof.reset_index()
        print(doof)
        return doof

    def on_message(self, ws, message):
        message = json.loads(message)
        asset = message['data']['s']
        t = message['data']['E'] # runtime
        p = float(message['data']['k']['o']) # current price
        c = message['data']['k']['x'] # closed yes or no?
        cp = float(message['data']['k']['c']) # last close price
        ct = message['data']['k']['T'] # close time
        tx = t - ct
        tx = timedelta(seconds = (ct-t)/1000)
        candle = message['data']['k']['i']
        
        if p >= self.exit_price:
            close_order = client.futures_create_order(symbol=self.sümbol, side='SELL', type='STOP_MARKET',stopPrice=self.exit_price)
            self.ws.close()
        elif p < self.entry_price & c == True:
            close_order = client.futures_create_order(symbol=self.sümbol, side='SELL', type='STOP_MARKET',stopPrice=self.entry_price)
            self.ws.close()

    def run_binance_websocket(self):
        self.ws.run_forever()
        

def reconnect_websocket():
    try:
        if not dws.connected:
            dws.connect('wss://gateway.discord.gg/?v=6&encording=json')
            # Reinitialize connection
    except:
        time.sleep(5)  # Wait for new connection attempt
        
        # Doc: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade 

        
        
# API Key:
        
# {'stream': 'btcusdt@kline_1m',
# 'data':
#   {"e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BTCUSDT",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BTCUSDT",  // Symbol
#     "i": "1m",      // Interval: m -> minutes; h -> hours; d -> days; w -> weeks; M -> months; 
#    1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
#     "B": "123456"   // Ignore
#     }
#   }
# }
