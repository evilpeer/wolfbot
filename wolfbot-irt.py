import time
import sqlite3
from os import system  #os operating system

def preguntar(condicion):
   if condicion == "ultimo":
      condicion = "DESC"
   if condicion == "primero":
      condicion = "ASC"

   buscar =  "SELECT start FROM candles_" + str(pair) + " ORDER BY start " + str(condicion) + " LIMIT 1"   
   resultado = list(dbh.execute(buscar))
   resultado = resultado[0]
   return (resultado[0])

### main ###
#y esto deberia pasarlo desde un archivo de configuracion
pair = "XBTUSD"
local_path = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python-bot"
dbfile = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-bot/con_base_de_datos/bitmex-5m.db"

#abro la base de  datos
conn = sqlite3.connect(dbfile)
dbh = conn.cursor()
date_last = preguntar("ultimo")

count = 0
while count == 0:
   time.sleep(5)
   ultimo = preguntar("ultimo") #pregunto si hubo cambio en la base de datos 
   if date_last != ultimo:
      date_last = ultimo
      fecha = str(time.strftime("%H:%M:%S"))
      print(str(time.ctime(int(date_last))) + ' ' + str(fecha) )   
      llamada = "python3.4 ./wolfbot-python.py " + str(date_last)   # aqui es donde se ejecutar el wolfbot-python
      system(llamada)


      

