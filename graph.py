import numpy as np
import pandas as pd
from talib import RSI, BBANDS
import matplotlib.pyplot as plt

import sqlite3
import configparser
import io

def load_ini():
   with open("config.ini") as f:
      file_config = f.read()
   config = configparser.RawConfigParser(allow_no_value=True)
   config.readfp(io.StringIO(file_config))
   return config

def sql_open(db_file):
   conn = None
   try:
      conn = sqlite3.connect(db_file)
   except Exception as e:
      print(e)
   return conn

def sql_query(siguiente, symbol):
   buscar = "SELECT * FROM candles_" + str(symbol) + " WHERE start = " + str(siguiente)
   resultado = dbh.execute(buscar)
   return resultado

def cargar_datos(symbol):
   global total
   global candle  #  Dentro de "candle" está la data en  este orden: timestamp, open, high, low, close, volume, vwp, trades 
   global price
   global timestamp
   candle = []
   price = []
   timestamp = []
   ultimo = date_last + 300
   total = 0
   for n in range(ultimo, date_first, -300):
      respuesta = sql_query(n, symbol)
      candles = respuesta.fetchall()
      total = total + 1
      for row in candles:
         temporal = []
         for o in range(2,9):
            temporal.append(row[o])
         timestamp.append(row[1])
         price.append(row[5])
         candle.append(temporal) # coño, al fin un solo arreglo con toda la data!
   total = total - 1

def bbp(price):
   up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
   bbp = (price['Close'] - low) / (up - low)
   return bbp

def rsi(price):
   rsi = RSI(close, timeperiod=14)
   return rsi

config = load_ini()                      # Leyendo el archivo de configuración y tomando los parametros correspondientes
number_coins = int(config.get('exchange', 'pairs'))
exchange = (config.get('exchange', 'name'))
aviable_pairs = exchange+".pairs"
coin = []
for n in range(0, number_coins):
   pair = "pair["+str(n+1)+"]"
   coin.append(config.get(aviable_pairs,pair))
local_path = (config.get('path', 'local_path'))
db_file = (config.get('path', 'db_path'))+(config.get('exchange', 'db_file'))
db_name = (config.get('sql', 'db_name'))

conn = sql_open(db_file)                 # abro la base de  datos y consulto el ultimo registro
dbh = conn.cursor()
                                         # Se puede hacer como bactrace pasando el ultimo timestamp a analizar y real-time
                                         # pasando el ultimo timestamp guardado
#date_last = int(sys.argv[1])             # paso el ultimo valor del timestamp a analizar
date_last = 1568919600

date_first = date_last - 86400           #un numero arbitrario por ahora
date_first = 1568772900
cargar_datos(coin[0])


# cutre... creo el dataframe de lo que sea que necesite
price = pd.DataFrame(candle, index=timestamp, columns =['Open', 'High', 'Low', 'Close', 'Volume', 'vwap', 'Trades']) 
#print(price)

#price = web.DataReader(name=symbol, data_source='quandl', start=start, end=end)
#price = candle.iloc[::-1]
#price = candle.dropna()
#             Open    High     Low   Close      Volume  ...     AdjOpen     AdjHigh      AdjLow    AdjClose   AdjVolume
#Date                                                    ...
#2015-01-02  111.39  111.44  107.35  109.33  53204626.0  ...  105.820966  105.868466  101.982949  103.863957  53204626.0

price = price.iloc[::-1]
price = price.dropna()
#print(price)
close = price['Close'].values
#print(close)

up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
print("BB (first low 10 elements)\n", low[20:30])
#rsi = RSI(close, timeperiod=14)
#print("RSI (first 10 elements)\n", rsi[14:24])
#print(rsi)


bbp = bbp(price)
price['BBP'] = bbp

rsi = rsi(price)
price['RSI'] = rsi

holdings = pd.DataFrame(index=price.index, data={'Holdings': np.array([np.nan] * price.index.shape[0])})
holdings.loc[((price['RSI'] < 20) & (price['BBP'] < 0)), 'Holdings'] = max_holding
holdings.loc[((price['RSI'] > 80) & (price['BBP'] > 1)), 'Holdings'] = 0
holdings.ffill(inplace=True)
holdings.fillna(0, inplace=True)
holdings['Order'] = holdings.diff()
holdings.dropna(inplace=True)
print(holdings)

print(price)
# ahora vamos a ver que sale con la visualizacion
fig, (ax0, ax1, ax2) = plt.subplots(3, 1, sharex=True, figsize=(12, 8))
ax0.plot(timestamp, price['Close'], label='Close')
ax0.invert_xaxis()
ax0.set_xlabel('Date')
ax0.set_ylabel('Close')
ax0.grid()

for day, holding in holdings.iterrows():
    order = holding['Order']
    if order > 0:
        ax0.scatter(x=day, y=price.loc[day, 'Close'], color='green')
        print(day)
    elif order < 0:
        ax0.scatter(x=day, y=price.loc[day, 'Close'], color='red')


ax1.plot(timestamp, price['RSI'], label='RSI')
ax1.fill_between(timestamp, y1=30, y2=70, color='#adccff', alpha='0.3')
ax1.set_xlabel('Date')
ax1.set_ylabel('RSI')
ax1.grid()

ax2.plot(timestamp, price['BBP'], label='BBP')
#ax2.plot(timestamp, price['Close'], label='Close')
#ax2.plot(timestamp, price['BB_low'], label='BB_low')
#ax2.fill_between(timestamp, y1=price['BB_low'], y2=price['BB_up'], color='#adccff', alpha='0.3')
ax2.set_xlabel('Date')
ax2.set_ylabel('Bollinger Bands')
ax2.grid()


fig.tight_layout()
plt.show()
