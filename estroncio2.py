#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-
import os, random, time, re
from pickle import STOP
import RPi.GPIO as GPIO
from test_LCD import lcd_byte		#este warning es porque RPi.GIPO es algo propio de la raspberry. Python no lo tiene.
GPIO.setmode(GPIO.BOARD)

#---------------------------------------------------------------------------------------------------------------
os.system("clear") #ESTO ES SOLO PARA LIMPIAR LA PANTALLA DURANTE LAS PRUEBAS Y QUE SE VEA BIEN LO QUE IMPRIME. Habría que borrarlo en el stadalone
#---------------------------------------------------------------------------------------------------------------
os.system("mpc clear") 									#Borro todo 
os.system("cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas") 	#Me paro en el dir donde están las canciones
os.system("mpc add /") 									#y vuelvo a cargar por si hay nuevas canciones
os.system("mpc crossfade") 								# Arranca con cossfade habilitado desgundos  
#Extraigo la cantidad de canciones que hay en la lista. En realidad cuenta la cantidad de archivos que hay en ese dir.Lo devuelve como un str y al parecer
#hay un archivo más, así que hay que castear a int y restarle 1.
largoListaCanciones_STR = os.popen('cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas/; ls -1 | wc -l') 
largoListaCanciones=((int((largoListaCanciones_STR.read()))))-1

#**********************************************************************************************
#										DEFINO LOS GPIO
#**********************************************************************************************
REPRODUCIR_PAUSA = 3
GPIO.setup(REPRODUCIR_PAUSA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ANTERIOR = 5
GPIO.setup(ANTERIOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SIGUIENTE = 7
GPIO.setup(SIGUIENTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PARAR = 11
GPIO.setup(PARAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SUBIR_VOLUMEN = 13
GPIO.setup(SUBIR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BAJAR_VOLUMEN = 15
GPIO.setup(BAJAR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_CROSSFADE = 19
GPIO.setup(CAMBIAR_CROSSFADE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_RANDOM = 21
GPIO.setup(CAMBIAR_RANDOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#--------------------------------------------------------------------------------------------
#		FIN DEFINICIÓN DE LOS GPIO
#--------------------------------------------------------------------------------------------

#***********************************************************************************************
#						DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0
HAY_ALGO_PARA_EJECUTAR = False	#Bandera
ALGUN_BOTON_APRETADO = False	#Otra bandera para saber si hay un botón apretado y quedarme esperando a que se suelte
TIEMPO_ANTIRREBOTES = 0.020		#20ms para la funcionr "no_rebote"
#--------------------------------------------------------------------------------------------
#					FIN DEFINICIÓN VARIABLES PARA LA MÁQUINA DE ESTADOS
#--------------------------------------------------------------------------------------------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():
    print("Iniciando estroncio...")
    start = time.time()
    global HAY_ALGO_PARA_EJECUTAR

    while(True):
        #esperar_liberar_botones()
        print("estoy aca afuera")
        if HAY_ALGO_PARA_EJECUTAR:					#
            os.system("mpc " + estado[indice])	    #
                                                    #
            HAY_ALGO_PARA_EJECUTAR = False			#
            ALGUN_BOTON_APRETADO = False
            print("estoy aca adentro")
            time.sleep(3)



#--------------------------------------------------------------------------------------------
#								Fin del programa principal								    #
#____________________________________________________________________________________________

################################################################################################
#											FUNCIONES										   #
################################################################################################

def leer_pulsadores(channel):
	global indice, HAY_ALGO_PARA_EJECUTAR
    
	if(not(GPIO.input(REPRODUCIR_PAUSA))):			#
		indice = 0									#En cuanto algún botón se presiona, se elimino la posibilidad de que sea un rebote
		print("indice 0")							#con la función antirrebotes. Si no es un rebote, en la función mismo se levanta una			
	elif(not(GPIO.input(ANTERIOR))):				#bandera para avisar que hay un botón apretado y se discrimina cuál es el botón presionado.
		indice = 1									#Los "NOT" son porque hay resistencias de pull up internas, por lo que las entradas están
		print("indice 1")							#en UNO por defecto. O sea, usa lógica negativa			
	elif(not(GPIO.input(SIGUIENTE))):				#
		indice = 2									#
		print("indice 2")
	elif(not(GPIO.input(PARAR))):					#
		indice = 3									#
		print("indice 3")
	elif(not(GPIO.input(SUBIR_VOLUMEN))):			#
		indice = 4									#
		print("indice 4")
	elif(not(GPIO.input(BAJAR_VOLUMEN))):			#
		indice = 5									#
		print("indice 5")
	elif(not(GPIO.input(CAMBIAR_CROSSFADE))):		#
		indice = 6									#
		print("indice 6")
	elif(not(GPIO.input(CAMBIAR_RANDOM))):			#
		indice = 7
		print("indice 7")

	HAY_ALGO_PARA_EJECUTAR = True

def esperar_liberar_botones():
	ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
					or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
					or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
					or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
					or not(GPIO.input(SUBIR_VOLUMEN)) 					#
					or not(GPIO.input(BAJAR_VOLUMEN)) 					#
					or not(GPIO.input(CAMBIAR_CROSSFADE))				#
					or not(GPIO.input(CAMBIAR_RANDOM)) 					#
					)
	while(ALGUN_BOTON_APRETADO):									#Si alguno de los otros pulsadores (sin ser el del encoder) está presionado, me quedo acá
		ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
				or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
				or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
				or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
				or not(GPIO.input(SUBIR_VOLUMEN)) 					#
				or not(GPIO.input(BAJAR_VOLUMEN)) 					#
				or not(GPIO.input(CAMBIAR_CROSSFADE))				#
				or not(GPIO.input(CAMBIAR_RANDOM)) 					#
				)
#--------------------------------------------------------------------------------------------
#								FIN DEFINICIÓN DE FUNCIONES
#--------------------------------------------------------------------------------------------

  ################################################################################################
#											INTERRUPCIONES										   #
  ################################################################################################
GPIO.add_event_detect(REPRODUCIR_PAUSA,	GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(ANTERIOR,			GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(SIGUIENTE,		GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(PARAR,			GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(SUBIR_VOLUMEN,	GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(BAJAR_VOLUMEN,	GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(CAMBIAR_CROSSFADE,GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
GPIO.add_event_detect(CAMBIAR_RANDOM,	GPIO.FALLING, callback = leer_pulsadores, bouncetime = 200)
#-----------------------------------------------------------------------------------------------
#								FIN DEFINICIÓN DE INTERRUPCIONES
#-----------------------------------------------------------------------------------------------

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	# finally:
	# 	pass
	# 	lcd_byte(0x01, LCD_CMD)
	# 	lcd_string("Goodbye!", LCD_LINE_1)
	# 	GPIO.cleanup()