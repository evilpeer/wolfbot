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
import configparser
import io

def load_ini():
   with open("config.ini") as f:
      file_config = f.read()
   config = configparser.RawConfigParser(allow_no_value=True)
   config.readfp(io.StringIO(file_config))
   return config

def time_format_8601(fecha):
   utc = str(datetime.utcfromtimestamp(fecha).isoformat())
   utc = utc[0:13] + "%3A" + utc[14:16] + "%3A" + utc[17:19] + ".000Z"
   return utc

def getdata_bitmex(utc, symbol):

   path = "/api/v1"
   function = "trade/bucketed"
   count = 1                            # numero de velas que me voy a arrastrar
   partial = "false"
   reverse = "false"
   binsize = "5m"                       # options 1m, 5m, 1h     este deberia arrastrarmelo desde linea de comandos
                                        # o mejor aun, traerme las velas de 1m y luego hacer la magia desde adentro

   headers = []
   buffer = io.BytesIO()
   params = "binSize="+binsize+"&partial="+partial+"&symbol="+symbol+"&count="+str(count)+"&reverse="+reverse+"&startTime="+utc
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
   except Exception as e:
      print(e)
   return conn

def sql_put(symbol):
   insertar = "INSERT INTO "+db_name+symbol+" (start, open, high, low, close, vwp, volume, trades) VALUES (?,?,?,?,?,?,?,?)"
   values = (timestamp, datos["open"], datos["high"], datos["low"], datos["close"], datos["vwap"], datos["volume"],datos["trades"])
   try:
      dbh = conn.cursor()
      dbh.execute(insertar,values)
      conn.commit()                        # esta es la orden de escribir....
   except Exception as e:                  # y este el manejo de la excepción
      print("ERROR: no se pudo escribir en la base de datos")
      print("SQL response: "+str(e))
   return


### main
                                        # ahora falta ver como manejar diferentes exchanges
config = load_ini()                     # Leyendo el archivo de configuración y tomando los parametros correspondientes
number_coins = int(config.get('exchange', 'pairs'))
exchange = (config.get('exchange', 'name'))
aviable_pairs = exchange+".pairs"
coin = []
for n in range(0, number_coins):
   pair = "pair["+str(n+1)+"]"
   coin.append(config.get(aviable_pairs,pair))
local_path = (config.get('path', 'local_path'))
db_path = (config.get('path', 'db_path'))
db_file = (config.get('path', 'db_path'))+(config.get('exchange', 'db_file'))
db_name = (config.get('sql', 'db_name'))
                                        # para generalizarlo a diferentes exchanges, esto deberia cambiar tambien 
                                        # porque cada exchange tiene su propia API
base_url = "https://"+(config.get('exchange', 'server'))

                                        # el verdadero catcher de datos empieza aqui

timestamp = int(sys.argv[1])            # paso el valor del timestamp el cual voy a actualizar
                                        # con esto puedo arrastrar data historica o el ultimo dato acumulado, a convenir
UTC = time_format_8601(timestamp)

for n in range(0, number_coins):        # Puedo capturar datos de multiples monedas en un mismo exchange
   datos = getdata_bitmex(UTC,coin[n])  # Esta funcion es especifica del exhange BITMEX y TESTNET, los otros requeriran otras funciones
   print(datos)
   conn = sql_open(db_file)             # abro la base de  datos
   sql_put(coin[n])
   # debo cerrar la base de datos
