Esta coleccion de archivos pretende llamarse
# WolfBot 
o la brevisima historia de
# Cómo no se me ocurrió un nombre mejor
 
Un intento por conseguir un bot para hacer transacciones en los exchanges con la menor intervención humana posible
Basado en python, shell scriting y sqlite3 

Una brevisima descripción de los archivos


      README.md
            Este archivo que intenta (con muy poco éxito) hacer algo de documentación.

      bitmex-5m.dat
            Archivo de salida de wolfbot-python.py, está puesto aqui sólo con caracter didáctico.
            Ha de suponerse que archivos siilares a este se irán generando mientras el bot esté en marcha.

      naive_bayes.py
            Un intento, un poco crudo aún,  de agregarle un predictor al bot, por ahora, no muy funcional.
            Aún así, un excelente ejercicio de programacion de inteligencia artificial asistida.
            Ya  está tomando  del archivo  de configuración  los parametros necesarios  para su  ejecución
         y recibiendo la llamada de ejecución desde el script principal.


      wolfbot-irt.py
            Ha  de suponerse que  este archivo revisa continuamente la base  de datos  en  espera  de  una
         actualización en tiempo real. (IRT).
            Cuando ocurre el evento, (por ahora, una vez cada 5 min.), éste pone en marcha los  siguientes
         niveles del bot.
            Ya está tomando del archivo de configuración los parametros necesarios para su ejecución.
            Tambien ejecuta de manera provisional el clasificador naive-bayes.

      wolfbot-python.py
            Se supone que aqui ocurre la magia.
            Pero  NO (todavia),  sólo lee en  la base de datos y genera  los  archivo "bitmex-5m.dat" para
         procesar la data con un análisis posterior  (del cual no tengo idea  de cómo lo voy a  hacer, por
         ahora).  Ya removí  del código el clasificador  bayesiano para  hacerlo  correr desde un  archivo
         diferente.  En éste punto  sólo tengo la lectura  de la data de un período  específico, aunque se
         debería poder ajustar el período de pre-procesamiento.
            Ya  está tomando  del archivo  de configuración  los parametros necesarios  para su  ejecución
         y recibiendo la llamada de ejecución desde el script principal.

       getdata-5m.py
            Con éste script pretendo  bajarme la data desde bitmex y escribirla en una base de datos local
         de manera continua, deberia estar ejecutandose desde el crontab, pero esa parte aun la debo.
            Ya está tomando del archivo de configuración los parametros necesarios para su ejecución.

       config.ini
            El archivo  de configuración  general del sistema,  desde aqui se ajustan  todas las variables
         necearias  para la configuración  de los mismos y así  evitamos tener que  editar cada uno de los
         scripts para cabiar cualquier configuración (nada nuevo bajo el sol)

       create_table.py
            Herramienta para crear el archivo de base de datos para nuestro sistema.
            Por ahora  sólo crearé la base de  datos de bitmex, con períodos de  5 minutos y con todas los
         criptoactivos que disponga bitmex en sus recursos

       crontab-5m.sh
            Un pequeño shell script para dispararlo desde el crontab cada 5 minutos

       integridad-5m.py
            Verifica la integridad de la  base de datos, busca y rellena  la data faltante  en caso de  que 
         existan, no  es parte de  sistema y  debe ejecutarse  sólo en caso  de que existan estas faltas de 
         continuidad.

