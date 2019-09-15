# Wolfbot para todos los procesos In Real Time (IRT)
# uno similar deberia programarse para hacer backtrace y evaluar estrategias


import time
import sqlite3
import configparser
import io
from os import system


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

def preguntar(condicion, symbol):       # pregutar quien es el ultimo o el primer registro en base de datos
   if condicion == "ultimo":
      condicion = "DESC"
   if condicion == "primero":
      condicion = "ASC"

   buscar =  "SELECT start FROM "+ db_name + symbol + " ORDER BY start " + str(condicion) + " LIMIT 1"   
   resultado = list(dbh.execute(buscar))
   resultado = resultado[0]
   return (resultado[0])

### main ###
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

conn = sql_open(db_file)                # abro la base de  datos y consulto el ultimo registro
dbh = conn.cursor()

date_last = preguntar("ultimo", coin[0])

count = 0
while count == 0:
   time.sleep(5)
   ultimo = preguntar("ultimo", coin[0])# reviso si hubo cambio en la base de datos 
   if date_last != ultimo:
      date_last = ultimo
      fecha = str(time.strftime("%H:%M:%S"))
      print(str(time.ctime(int(date_last))) + ' ' + str(fecha) )  
                                        # aqui es donde hago un llamado al sistema para ejecutar el wolfbot-python 
      llamada = "python3.4 ./wolfbot-python.py " + str(date_last)  
      system(llamada)


      

