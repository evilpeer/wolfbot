# Naive Bayes implemented from Scratch in Python
import csv
import random
import math
import sqlite3
import sys
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
   buscar = "SELECT * FROM "+db_name+symbol+ " WHERE start = " + str(siguiente)
   resultado = dbh.execute(buscar)
   return resultado

def cargar_datos(symbol):
   global total
   candle = []
   dataset = []
   ultimo = date_last + 300
   total = 0
   for n in range(date_first, ultimo, 300):
      respuesta = sql_query(n, symbol)
      candles = respuesta.fetchall()
      total = total + 1
      for row in candles:
         temporal = []
         for o in range(0,9):
            temporal.append(row[o])
         candle.append(temporal) # coño, al fin un solo arreglo con toda la data!
   total = total - 1


   # en este tramo acondiciono los datos para procesarlos con naive-bayes
   for n in range(0, total-9):
      temporal = []
#esto está un poquitin cutre, pero esta funcionando
      temporal.append(candle[n][2]-candle[n][7])
      temporal.append(candle[n][3]-candle[n][7]) 
      temporal.append(candle[n][4]-candle[n][7])  
      temporal.append(candle[n][5]-candle[n][7])  
      temporal.append(candle[n][7])
      temporal.append(candle[n][8])

      for o in range(n, n+9):
         if candle[o][5] > (candle[n][5]+((candle[n][5]*0.5)/100)):
            flag = 1
            break
         if candle[o][5] < ((candle[n][5])-((candle[n][5]*0.5)/100)):
            flag = -1
            break
         flag = 0
      temporal.append(flag)
      dataset.append(temporal)
   return dataset

def splitDataset(dataset, splitRatio):
	trainSize = int(len(dataset) * splitRatio)
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

#main

config = load_ini()                  # Leyendo el archivo de configuración y tomando los parametros correspondientes
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
conn = sql_open(db_file)             # abro la base de  datos y consulto el ultimo registro
dbh = conn.cursor()


splitRatio = 0.9
date_last = int(sys.argv[1])        # paso el ultimo valor del timestamp a analizar o el valor del backtrace
#date_last = 1568641800 

date_first = date_last - 1467000;    # un numero arbitrario por ahora
#date_first = date_last - 3600;         #un numero arbitrario por ahora

# load the data
dataset = cargar_datos(coin[0])

# pre-process the data
trainingSet, testSet = splitDataset(dataset, splitRatio)
#print("split "+str(len(dataset))+" rows into train="+str(len(trainingSet))+" and test="+str(len(testSet))+" rows") 

# prepare model
summaries = summarizeByClass(trainingSet)

# test model
predictions = getPredictions(summaries, testSet)
accuracy = getAccuracy(testSet, predictions)
#print("Accuracy: "+str(accuracy)+"%")

#Ahora a ver como leo el ultimo valor "date_first" (esto se puede "limpiar" muchisismo)
quest = sql_query(date_last, coin[0])
evaluate_candle = quest.fetchall()
temporal = []
inputtest = []


#esto está un poquitin cutre, pero esta funcionando
temporal.append(evaluate_candle[0][2]-evaluate_candle[0][7])
temporal.append(evaluate_candle[0][3]-evaluate_candle[0][7]) 
temporal.append(evaluate_candle[0][4]-evaluate_candle[0][7])  
temporal.append(evaluate_candle[0][5]-evaluate_candle[0][7])  
temporal.append(evaluate_candle[0][7])
temporal.append(evaluate_candle[0][8])
inputtest.append(temporal)
predictions = getPredictions(summaries, inputtest)


print("split "+str(len(dataset))+" rows into train="+str(len(trainingSet))+" and test="+str(len(testSet))+" rows"+" Accuracy: "+str(accuracy)+"% Prediction: "+(str(predictions))) 


	
#main()
