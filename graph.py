import numpy as np
import pandas as pd
from talib import RSI, BBANDS, STOCH
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
#   ultimo = date_last + 300
   total = 0
   for n in range(date_last, date_first-300, -300):
#   for o in range(date_first, (date_last+300), 300):
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
   print(total)
def bbp():
   up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2.5, nbdevdn=2.5, matype=8)
#   up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
#   bbp = (price['Close'] - low) / (up - low)
   bbp = (close - low) / (up - low)
   return bbp,up,mid,low

def rsi():
   rsi = RSI(close, timeperiod=14)
   return rsi

def stoch():
   mediak = []
   mediad = []
   slowk, slowd = STOCH(high, low, close, fastk_period=14, slowk_period=1, slowk_matype=1, slowd_period=3, slowd_matype=1)
   for n in range(0, (total+1)):

      if n < 5:
         mediak.append(slowk[n])
         mediad.append(slowd[n])
      else:
         mediak.append((slowk[n]+slowk[n-1]+slowk[n-2]+slowk[n-3]+slowk[n-4])/5)
         mediad.append((slowd[n]+slowd[n-1]+slowd[n-2]+slowd[n-3]+slowd[n-4])/5)
   return slowk, slowd, mediak, mediad


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
date_last = 1569078300

date_first = date_last - 86400           #un numero arbitrario por ahora
#date_first = 1568920200
#date_first = 1568790600
cargar_datos(coin[0])


# cutre... creo el dataframe de lo que sea que necesite
price = pd.DataFrame(candle, index=timestamp, columns =['Open', 'High', 'Low', 'Close', 'Volume', 'vwap', 'Trades']) 
price = price.iloc[::-1]
price = price.dropna()

high  = price['High'].values
low   = price['Low'].values
close = price['Close'].values

#bollinger
bbp,up,mid,low = bbp()
price['BBP'] = bbp
price['BB_up'] = up
price['BB_mid'] = mid
price['BB_low'] = low

#RSI
rsi = rsi()
price['RSI'] = rsi

#STOCH
slowk, slowd, mediak, mediad = stoch()
price['ST_slowK'] = slowk
price['ST_slowD'] = slowd
price['ST_mediaK'] = mediak
price['ST_mediaD'] = mediad



max_holding = 100
holdings = pd.DataFrame(index=price.index, data={'Holdings': np.array([np.nan] * price.index.shape[0])})
holdings.loc[((price['RSI'] < 20) & (price['BBP'] < 0)), 'Holdings'] = max_holding
holdings.loc[((price['RSI'] > 80) & (price['BBP'] > 1)), 'Holdings'] = 0
#holdings.loc[((price['RSI'] < 30) & (price['BBP'] < 0)), 'Holdings'] = max_holding
#holdings.loc[((price['RSI'] > 70) & (price['BBP'] > 1)), 'Holdings'] = 0
holdings.ffill(inplace=True)
holdings.fillna(0, inplace=True)
holdings['Order'] = holdings.diff()
holdings.dropna(inplace=True)

#print(price)

#print(holdings)

print(price)
# ahora vamos a ver que sale con la visualizacion
fig, (ax0, ax1, ax2) = plt.subplots(3, 1, sharex=True, figsize=(12, 8))
ax0.plot(timestamp, price['Close'].values, label='Close')
ax0.invert_xaxis()
ax0.set_xlabel('Date')
ax0.set_ylabel('Close')
ax0.grid()

for day, holding in holdings.iterrows():
    order = holding['Order']
    if order > 0:
        ax0.scatter(x=(date_first+(date_last-day))+300, y=price.loc[day, 'Close'], color='green')
    elif order < 0:
        ax0.scatter(x=(date_first+(date_last-day))+300, y=price.loc[day, 'Close'], color='red')


#ax1.plot(timestamp, price['RSI'], label='RSI')
ax1.plot(timestamp, price['ST_mediaK'], label='ST_Media_K')
ax1.plot(timestamp, price['ST_mediaD'], label='ST_Media_D')
#ax1.fill_between(timestamp, y1=70, y2=30, color='#adccff', alpha='0.3')
#ax1.fill_between(timestamp, y1=80, y2=20, color='#adccff', alpha='0.3')
ax1.set_xlabel('Date')
ax1.set_ylabel('Stock')
ax1.grid()

#ax2.plot(timestamp, price['BBP'], label='BBP')
ax2.plot(timestamp, price['BB_up'], label='BB_up')
ax2.plot(timestamp, price['Close'], label='Close')
ax2.plot(timestamp, price['BB_mid'], label='BB_mid')
ax2.plot(timestamp, price['BB_low'], label='BB_low')

ax2.fill_between(timestamp, y1=price['BB_low'], y2=price['BB_up'], color='#adccff', alpha='0.3')
ax2.set_xlabel('Date')
ax2.set_ylabel('Bollinger Bands')
ax2.grid()


fig.tight_layout()
plt.show()
