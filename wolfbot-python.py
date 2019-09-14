# he aqui quien procesa la data contenida
# se puede usar IRT o Bactrace, dependiendo de el parametro que debe pasarse por la linea de cmandos
# se pasa por parametro en la linea de comandos el unix time del punto a evaluar
# por ahora, la base de datos esta escrita para almacenar velas en periodos de 5m, eso sera modificado (heredado del ancho de banda)


import sqlite3
import sys
import csv
import random
import math

def sql_query(siguiente):
   buscar = "SELECT * FROM candles_" + str(pair) + " WHERE start = " + str(siguiente)
   resultado = dbh.execute(buscar)
   return resultado

def cargar_datos():
   global total
   global candle  #  Dentro de "candle" está la data en  este orden: timestamp, open, high, low, close, volume, vwp, trades 
   candle = []
   ultimo = date_last + 300
   total = 0
   for n in range(date_first, ultimo, 300):
      respuesta = sql_query(n)
      candles = respuesta.fetchall()
      total = total + 1
      for row in candles:
         temporal = []
         for o in range(1,9):
            temporal.append(row[o])
         candle.append(temporal) # coño, al fin un solo arreglo con toda la data!
   total = total - 1

##### injerto proveniente de naive_bayes.py

def loadCsv(filename):
	lines = csv.reader(open(filename, "r"))
	dataset = list(lines)
	for i in range(len(dataset)):
		dataset[i] = [float(x) for x in dataset[i]]
	return dataset

def splitDataset(dataset, splitRatio):
#	trainSize = int(len(dataset) * splitRatio)
	trainSize = int(len(dataset) - 5)
	trainSet = []
	copy = list(dataset)
	while len(trainSet) < trainSize:
		index = random.randrange(len(copy))
		trainSet.append(copy.pop(index))
	return [trainSet, copy]

def separateByClass(dataset):  #separo los que tienen (1) de los que no (0) en dos campos del list
	separated = {}
	for i in range(len(dataset)):
		vector = dataset[i]
		if (vector[-1] not in separated):
			separated[vector[-1]] = []
		separated[vector[-1]].append(vector)
	return separated

def mean(numbers):
	return sum(numbers)/float(len(numbers))

def stdev(numbers):
	avg = mean(numbers)
	variance = sum([pow(x-avg,2) for x in numbers])/float(len(numbers)-1)
	return math.sqrt(variance)

def summarize(dataset):
	summaries = [(mean(attribute), stdev(attribute)) for attribute in zip(*dataset)]
	del summaries[-1]
	return summaries

def summarizeByClass(dataset):
	separated = separateByClass(dataset)
	summaries = {}
	for classValue, instances in separated.items():
		summaries[classValue] = summarize(instances)
	return summaries

def calculateProbability(x, mean, stdev):
	exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
	return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent

def calculateClassProbabilities(summaries, inputVector):
	probabilities = {}
	for classValue, classSummaries in summaries.items():
		probabilities[classValue] = 1
		for i in range(len(classSummaries)):
			mean, stdev = classSummaries[i]
			x = inputVector[i]
			probabilities[classValue] *= calculateProbability(x, mean, stdev)
	return probabilities
			
def predict(summaries, inputVector):
	probabilities = calculateClassProbabilities(summaries, inputVector)
	bestLabel, bestProb = None, -1
	for classValue, probability in probabilities.items():
		if bestLabel is None or probability > bestProb:
			bestProb = probability
			bestLabel = classValue
	return bestLabel

def getPredictions(summaries, testSet):
	predictions = []
	for i in range(len(testSet)):
		result = predict(summaries, testSet[i])
		predictions.append(result)
	return predictions

def getAccuracy(testSet, predictions):
	correct = 0
	for i in range(len(testSet)):
		if testSet[i][-1] == predictions[i]:
			correct += 1
	return (correct/float(len(testSet))) * 100.0



### main ###

#esto deberia pasarlo desde un archivo de configuracion
pair = "XBTUSD"
local_path = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python-bot"
dbfile = "/home/tortuga/crypto/prices/tradebot/bitmex/bitmex-bot/con_base_de_datos/bitmex-5m.db"

#abro la base de  datos
conn = sqlite3.connect(dbfile)
dbh = conn.cursor()

# Se puede hacer como bactrace pasando el ultimo timestamp a analizar y real-time pasando el ultimo timestamp guardado
date_last = int(sys.argv[1])   # paso el ultimo valor del timestamp a analizar

date_first = date_last - 146700;  #un numero arbitrario por ahora
cargar_datos()

# esto esta aqui solo de adorno pa ver si funciona la vaina
print(" timestamp    open    high     low   close    volume        vwp trades")
print((str(candle[total][0]))+" "+(str(candle[total][1]))+" "+(str(candle[total][2]))+" "+(str(candle[total][3]))+" "+(str(candle[total][4]))+" "+(str(candle[total][5]))+" "+(str(candle[total][6]))+" "+(str(candle[total][7])))

# ahora escribo el archivo que necesito para la grafica y los calculos que vienen 
bitmex_dat = open("./bitmex-5m.dat", "w")
for n in range(0, total+1):
   linea = (str(candle[n][0])+","+str(candle[n][1])+","+str(candle[n][2])+","+str(candle[n][3])+","+str(candle[n][4])+","+str(candle[n][5])+","+str(candle[n][6])+","+str(candle[n][7]))
   bitmex_dat.write(str(linea) + '\n')
bitmex_dat.close()


#cochinon esta parte, solo me interesa que camine, la elegancia al carajo
# timestamp, open, high, low, close, volume, vwp, trades 
bitmex_pre = open("./bitmex-5m.csv", "w")
for n in range(0, total-9):
   linea = ""
   temp =candle[n][1]-candle[n][6]  
   linea = linea + str(temp)
   temp =candle[n][2]-candle[n][6]  
   linea = linea + "," + str(temp)
   temp =candle[n][3]-candle[n][6]  
   linea = linea + "," + str(temp)
   temp =candle[n][4]-candle[n][6]  
   linea = linea + "," + str(temp) + "," + str(candle[n][5]) + "," + str(candle[n][7])
   for o in range(n, n+9):
      if candle[o][4] > (candle[n][4]+((candle[n][4]*0.5)/100)):
         flag = 1
         break
      if candle[o][4] < ((candle[n][4])-((candle[n][4]*0.5)/100)):
         flag = -1
         break
      flag = 0
   linea = linea + "," + (str(flag))
   bitmex_pre.write(str(linea) + '\n')
bitmex_pre.close()



dataset = []
inputtest = []
linea = ""
temp =candle[total][1]-candle[total][6] 
dataset.append(temp)
linea = linea + str(temp)
temp =candle[total][2]-candle[total][6]  
dataset.append(temp)
linea = linea + "," + str(temp)
temp =candle[total][3]-candle[total][6]  
dataset.append(temp)
linea = linea + "," + str(temp)
temp =candle[total][4]-candle[total][6]  
dataset.append(temp)
dataset.append(candle[total][5])
dataset.append(candle[total][7])
dataset.append(1)

linea = linea + "," + str(temp) + "," + str(candle[total][5]) + "," + str(candle[total][7])
linea = linea + "," + (str(flag))
inputtest.append(dataset)

##### injerto
filename = 'bitmex-5m.csv'
splitRatio = 0.67
dataset = loadCsv(filename)
trainingSet, testSet = splitDataset(dataset, splitRatio)
# prepare model
summaries = summarizeByClass(trainingSet)
# test model
predictions = getPredictions(summaries, testSet)
        
accuracy = getAccuracy(testSet, predictions)
predictions = getPredictions(summaries, inputtest)
print("Prediction: " + str(predictions) + " Accuracy: " + str(accuracy) + "%")
exit()




