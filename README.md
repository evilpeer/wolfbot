Esta coleccion de archivos pretende llamarse
# WolfBot 
o la brevisima historia de
# Cómo no se me ocurrió un nombre mejor
 
Un intento por conseguir un bot para hacer transacciones en los exchanges con la menor intervención humana posible
Basado en python, shell scriting y sqlite3 

Una brevisima descripción de los archivos


      README.md
            Este archivo que intenta (con muy poco éxito) hacer algo de documentación.

      bitmex-5m.csv
            Archivo de salida de wolfbot-python.py, está puesto aqui sólo con caracter didáctico.
            Ha de suponerse que archivos siilares a este se irán generando mientras el bot esté en marcha.

      naive_bayes.py
            Un intento, un poco crudo aún,  de agregarle un predictor al bot, por ahora, no muy funcional.
            Aún así, un excelente ejercicio de programacion de inteligencia artificial asistida.

      wolfbot-irt.py
            Ha  de suponerse que  este archivo revisa continuamente la base  de datos  en  espera  de  una
         actualización en tiempo real. (IRT).
            Cuando ocurre el evento, (por ahora, una vez cada 5 min.), éste pone en marcha los  siguientes
         niveles del bot.

      wolfbot-python.py
            Se supone que aqui ocurre la magia.
            Pero  NO (todavia), sólo lee  en la base de datos  y  genera  los  archivo  "bitmex-5m.dat"  y 
         "bitmex.csv" con data pre-procesada para un análisis posterior (del cual no tengo idea de cómo lo
         voy a hacer, por ahora).  En éste punto del desarrollo, tiene  empotrado dentro del código de una
         manera   ex-tre-ma-da-men-te  cutre  la  implementación   del   clasificador   bayesiano  ingenuo
         (naive-bayes) pero esa vaina va a salir de ahi quien sabe para donde. (continuará)... 

       getdata-5m.py
            Con éste script pretendo  bajarme la data desde bitmex y escribirla en una base de datos local
         de manera continua, deberia estar ejecutandose desde el crontab, pero esa parte aun la debo.

       config.ini
            El archivo  de configuración  general del sistema,  desde aqui se ajustan  todas las variables
         necearias  para la configuración  de los mismos y así  evitamos tener que  editar cada uno de los
         scripts para cabiar cualquier configuración (nada nuevo bajo el sol)


