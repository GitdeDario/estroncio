#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-

import os, random, time, re
from pickle import STOP
import RPi.GPIO as GPIO
from test_LCD import lcd_byte		#este warning es porque RPi.GIPO es algo propio de la raspberry. Python no lo tiene.
GPIO.setmode(GPIO.BOARD)

#---------------------------------------------------------------------------------------------------------------
os.system("clear") #ESTO ES SOLO PARA LIMPIAR LA PANTALLA DURANTE LAS PRUEBAS Y QUE SE VEA BIEN LO QUE IMPRIME. 
		   #SE BORRARÍA EN EL PROGRAMA DE PRODUCCIÓN.
#---------------------------------------------------------------------------------------------------------------
os.system("mpc clear") #Borro todo 
os.system("cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas") #Me paro en el dir donde están las canciones
os.system("mpc add /") #y vuelvo a cargar por si hay nuevas canciones
os.system("mpc crossfade") # Arranca con cossfade habilitado desgundos  
#Extraigo la cantidad de canciones que hay en la lista. En realidad cuenta la cantidad de archivos que hay en ese dir.Lo devuelve como un str y al parecer
#hay un archivo más, así que hay que castear a int y restarle 1.
largoListaCanciones_STR = os.popen('cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas/; ls -1 | wc -l') 
largoListaCanciones=((int((largoListaCanciones_STR.read()))))-1

#*********************************************************************************************
#		DEFINO LOS GPIO
# Estas van en español porque después uso "lo mismo" para la maquina de edos, pero en inglés
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
#	DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************


#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0

HAY_ALGO_PARA_EJECUTAR = False

TIEMPO_ANTIRREBOTES = 0.020	#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1		#1 segundo para que recargar datos de la pista que se está reproduciendo




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():
	print("Se inicia el programa........")
	start = time.time()

	song = random.randint(1,largoListaCanciones)
	os.system("mpc play" +" "+ str(song)) ###################BORRAR ESTO!!!!!!!!!!!!!!!!!!!!!!!!!

	while(True):
		HAY_ALGO_PARA_EJECUTAR = leer_pulsadores()	#Consulto los pulsadores y veo si hay alguno apretado
		espero_a_que_se_libere_el_pulsador()

		if HAY_ALGO_PARA_EJECUTAR:	
			os.system("mpc"+" "+estado[indice])				#
			HAY_ALGO_PARA_EJECUTAR = False			#

		
			
#--------------------------------------------------------------------------------------------
#								Fin del programa principal								    #
#____________________________________________________________________________________________

################################################################################################
#											FUNCIONES										   #
################################################################################################

def	no_rebote(boton):					#Antirrebotes.
	boton_antes = GPIO.input(boton)		#Recibe el número del gpio (el botón) presionado
	time.sleep(TIEMPO_ANTIRREBOTES)		#elimina rebotes y si está todo OK, levanta la 
	boton_despues = GPIO.input(boton)	#bandera avisando que hay algún botón apretado
										#
	if(boton_antes == boton_despues):	#
		return True						#
	else:								#
		return False					#

def leer_pulsadores():
	global indice
	if(not(GPIO.input(REPRODUCIR_PAUSA))):			#
		if(no_rebote(REPRODUCIR_PAUSA)):			#En cuanto algún botón se presiona, se elimino la posibilidad de que sea un rebote
			indice = 0								#con la función antirrebotes. Si no es un rebote, en la función mismo se levanta una
			return True
	elif(not(GPIO.input(ANTERIOR))):				#bandera para avisar que hay un botón apretado y se discrimina cuál es el botón presionado.
		if(no_rebote(ANTERIOR)):					#Los "NOT" son porque hay resistencias de pull up internas, por lo que las entradas están
			indice = 1								#en UNO por defecto. O sea, usa lógica negativa
			return True
	elif(not(GPIO.input(SIGUIENTE))):				#
		if(no_rebote(SIGUIENTE)):					#Los break son para que si se presiona más de un botón a la vez, se tome en cuent
			indice = 2								#solo el primero que se apretó			
			return True		
	elif(not(GPIO.input(PARAR))):					#
		if(no_rebote(PARAR)):						#
			indice = 3
			return True
	elif(not(GPIO.input(SUBIR_VOLUMEN))):			#
		if(no_rebote(SUBIR_VOLUMEN)):				#
			indice = 4
			return True
	elif(not(GPIO.input(BAJAR_VOLUMEN))):			#
		if(no_rebote(BAJAR_VOLUMEN)):				#
			indice = 5
			return True
	elif(not(GPIO.input(CAMBIAR_CROSSFADE))):		#
		if(no_rebote(CAMBIAR_CROSSFADE)):			#
			indice = 6
			return True
	elif(not(GPIO.input(CAMBIAR_RANDOM))):			#
		if(no_rebote(CAMBIAR_RANDOM)):				#
			indice = 7
			return True

def espero_a_que_se_libere_el_pulsador():
	ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
					or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
					or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
					or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
					or not(GPIO.input(SUBIR_VOLUMEN)) 					#
					or not(GPIO.input(BAJAR_VOLUMEN)) 					#
					or not(GPIO.input(CAMBIAR_CROSSFADE))				#
					or not(GPIO.input(CAMBIAR_RANDOM)) 					#
					)
	while(ALGUN_BOTON_APRETADO):
			ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
					or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
					or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
					or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
					or not(GPIO.input(SUBIR_VOLUMEN)) 					#
					or not(GPIO.input(BAJAR_VOLUMEN)) 					#
					or not(GPIO.input(CAMBIAR_CROSSFADE))				#
					or not(GPIO.input(CAMBIAR_RANDOM)) 					#
					)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	# finally:
		# lcd_byte(0x01, LCD_CMD)
		# lcd_string("Goodbye!", LCD_LINE_1)
		# GPIO.cleanup()