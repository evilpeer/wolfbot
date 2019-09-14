# pip install pycurl (requiere pycurl)
# getdata es la parte del software que arrastra la data desde el servidor bitmex y construye la base de  datos
# lo idea seria tener una por cada exchange en el cual se quiera operar
# debo consruir tambien la que corresponde a poloniex y algun otro exhange a conveniencia
# 
# Esta parte del software no deberia tener ninguna opcion para operar con ella
# solo debe ser llamada desde el cron cada cierto tiempo para que se ejecute convenientemente
# 
# definitivamente (como todo coder) soy una mierda para documentar  

import time
import sqlite3
from datetime import datetime
import sys
import pycurl
import io
import json

def time_format_8601(fecha):
   utc = str(datetime.utcfromtimestamp(fecha).isoformat())
   utc = utc[0:13] + "%3A" + utc[14:16] + "%3A" + utc[17:19] + ".000Z"
   return utc

def getdata(utc):
   headers = []
   buffer = io.BytesIO()
   params = "binSize="+binsize+"&partial="+partial+"&symbol="+pair+"&count="+str(count)+"&reverse="+reverse+"&startTime="+utc
   url = base_url + path + "/" + function + "?" + params
#   nonce = nonc()
   headers.append('Connection: Keep-Alive')
   headers.append('Keep-Alive: 90')
   curl = pycurl.Curl()
   curl.setopt(pycurl.URL, url)
   curl.setopt(pycurl.SSL_VERIFYPEER, 0)
   curl.setopt(pycurl.HTTPHEADER, headers)
   curl.setopt(pycurl.WRITEDATA, buffer)
   curl.perform()
   curl.close()
   response_body = buffer.getvalue().decode('utf-8')
   response_body = response_body[1:-1]       # remuevo el primer y ultimo caracter, el json tiene una malformacion por estos caracteres
   response = json.loads(response_body)
   return response

def nonc():
   nonce = int((time.time() * 1000000) + 1)
   return nonce

def sql_open(db_file):
   conn = None
   try:
      conn = sqlite3.connect(db_file)
   except Error as e:
      print(e)
   return conn

def sql_put():
   insertar = "INSERT INTO candles_"+pair+" (start, open, high, low, close, vwp, volume, trades) VALUES (?,?,?,?,?,?,?,?)"
   values = (timestamp, datos["open"], datos["high"], datos["low"], datos["close"], datos["vwap"], datos["volume"],datos["trades"])
   dbh = conn.cursor()
   dbh.execute(insertar,values)
#   resultado = dbh.execute(insertar,values)
#   respuesta = resultado.fetchall()
   conn.commit()                        # esta es la orden de escribir....
# aqi hace falta una excepcion para cuando haya alguna falla en la escritura del registro
   return


### main
pair = "XBTUSD"                         # si voy a consultar alguna otra divisa, esto debe cambiarse segun se requiera
local_path = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python-bot"
dbfile = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-bot/con_base_de_datos/bitmex-5m.db"

base_url = "https://www.bitmex.com"
path = "/api/v1"
function = "trade/bucketed"
count = 1                               # numero de velas que me voy a arrastrar
partial = "false"
reverse = "false"
binsize = "5m"                          # options 1m, 5m, 1h     este deberia arrastrarmelo desde linea de comandos
                                        # o mejor aun, traerme las velas de 1m y luego hacer la magia desde adentro

timestamp = int(sys.argv[1])            # paso el valor del timestamp el cual voy a actualizar
                                        # con esto puedo arrastrar data historica o el ultimo dato acumulado, a convenir
UTC = time_format_8601(timestamp)
datos = getdata(UTC)

conn = sql_open(dbfile)                 # abro la base de  datos
sql_put()


