#este es el esquema general de la tabla de base de datos
#CREATE TABLE candles_XBTUSD (
#        id INTEGER PRIMARY KEY AUTOINCREMENT,
#        start INTEGER UNIQUE,
#        open REAL NOT NULL,
#        high REAL NOT NULL,
#        low REAL NOT NULL,
#        close REAL NOT NULL,
#        vwp REAL NOT NULL,
#        volume REAL NOT NULL,
#        trades INTEGER NOT NULL);
import sqlite3


def sql_open(db_file):
   conn = None
   try:
      conn = sqlite3.connect(db_file)
   except Exception as e:
      print(e)
   return conn

def sql_create(symbol):
   crear = "\
   CREATE TABLE candles_"+str(symbol)+"(\n \
        id INTEGER PRIMARY KEY AUTOINCREMENT,\n \
        start INTEGER UNIQUE,\n \
        open REAL NOT NULL,\n \
        high REAL NOT NULL,\n \
        low REAL NOT NULL,\n \
        close REAL NOT NULL,\n \
        vwp REAL NOT NULL,\n \
        volume REAL NOT NULL,\n \
        trades INTEGER NOT NULL)\n"
   resultado = dbh.execute(crear)
   return resultado

#Los criptoactivos dispnibles en bitmex
#XBTUSD ETHUSD ADAU19 BCHU19 EOSU19 LTCU19 TRXU19 XRPU19

db_file = "./bitmex-5m.db"
bitmex_dat = open(db_file, "w")
bitmex_dat.write('')
bitmex_dat.close()

conn = sql_open(db_file)                # abro la base de  datos y consulto el ultimo registro
dbh = conn.cursor()

list_coins = ["XBTUSD","ETHUSD","ADAU19","BCHU19","EOSU19","LTCU19","TRXU19","XRPU19"]

for item in list_coins:
   resultado=sql_create(item)

