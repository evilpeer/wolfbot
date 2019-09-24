# he aqui quien procesa la data contenida
# se puede usar IRT o Bactrace, dependiendo de el parametro que debe pasarse por la linea de cmandos
# se pasa por parametro en la linea de comandos el unix time del punto a evaluar
# por ahora, la base de datos esta escrita para almacenar velas en periodos de 5m, eso sera modificado (heredado del ancho de banda)


import sqlite3
import sys
import csv
import random
import math
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
   candle = []
   ultimo = date_last + 300
   total = 0
   for n in range(date_first, ultimo, 300):
      respuesta = sql_query(n, symbol)
      candles = respuesta.fetchall()
      total = total + 1
      for row in candles:
         temporal = []
         for o in range(1,9):
            temporal.append(row[o])
         candle.append(temporal) # coño, al fin un solo arreglo con toda la data!
   total = total - 1

### main ###

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
print(local_path)
conn = sql_open(db_file)                 # abro la base de  datos y consulto el ultimo registro
dbh = conn.cursor()
                                         # Se puede hacer como bactrace pasando el ultimo timestamp a analizar y real-time
                                         # pasando el ultimo timestamp guardado
date_last = int(sys.argv[1])             # paso el ultimo valor del timestamp a analizar

date_first = date_last - 146700;         #un numero arbitrario por ahora
cargar_datos(coin[0])

# esto esta aqui solo de adorno pa ver si funciona la vaina
print(" timestamp    open    high     low   close    volume        vwp trades")
print((str(candle[total][0]))+" "+(str(candle[total][1]))+" "+(str(candle[total][2]))+" "+(str(candle[total][3]))+" "+(str(candle[total][4]))+" "+(str(candle[total][5]))+" "+(str(candle[total][6]))+" "+(str(candle[total][7])))

                                         # ahora escribo el archivo que necesito para la grafica y los calculos que vienen 
datos = local_path + "bitmex-5m.dat"
bitmex_dat = open(datos, "w")
for n in range(0, total+1):
   linea = (str(candle[n][0])+","+str(candle[n][1])+","+str(candle[n][2])+","+str(candle[n][3])+","+str(candle[n][4])+","+str(candle[n][5])+","+str(candle[n][6])+","+str(candle[n][7]))
   bitmex_dat.write(str(linea) + '\n')
bitmex_dat.close()
exit()

#falta traducir esta parte de perl a python, basicamente porque las herramientas no las he programado
#   my $ema_backtrace = join "", ("/usr/bin/perl ", $local_path, "/ema-5m.pl "); 
#   open(BACKTRACE,"|$ema_backtrace");
#   close(BACKTRACE);

#   my $image_backtrace = join "", ("/usr/bin/perl ", $local_path, "/image-5m.pl "); 
#   open(BACKTRACE,"|$image_backtrace");
#   close(BACKTRACE);
#   if ($timestamp[$incremental] == $UNX_date_last){$ciclo = 1}
#   $incremental++;
#   sleep 2;
#   }

#exit();


