#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-

import os, random, time
import RPi.GPIO as GPIO
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
# Estas van en inglés para no entreverarlas con las def de GPIO que se llaman "igual"
#************************************************************************************************
PLAY_PAUSE = PREV = NEXT = STOP = VOL_UP = VOL_DOWN = TOGGLE_CROSSFADE = TOGGLE_RANDOM = False

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0

HAY_ALGO_PARA_EJECUTAR = False

ALGUN_BOTON_APRETADO = False

TIEMPO_ANTIRREBOTES = 0.020	#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1		#1 segundo para que recargar datos de la pista que se está reproduciendo




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():
	global ALGUN_BOTON_APRETADO
	print("Se inicia el programa........")
	start = time.time()

	song = random.randint(1,largoListaCanciones)
	os.system("mpc play") ###################BORRAR ESTO!!!!!!!!!!!!!!!!!!!!!!!!!

	while(True):
		while(not ALGUN_BOTON_APRETADO):					#Mientras no haya ningún botón apretado, me quedo leyendo lanentrada
			if(not(GPIO.input(REPRODUCIR_PAUSA))):			#
				if(no_rebote(REPRODUCIR_PAUSA)):			#
					PLAY_PAUSE = True						#En cuanto algún botón se presiona, se elimino la posibilidad de que sea un rebote
					indice = 0
	#				print("PLAY")							#con la función antirrebotes. Si no es un rebote, en la función mismo se levanta una
					break									#
			elif(not(GPIO.input(ANTERIOR))):				#bandera para avisar que hay un botón apretado y se discrimina cuál es el botón presionado.
				if(no_rebote(ANTERIOR)):					#
					PREV = True								#Los "NOT" son porque hay resistencias de pull up internas, por lo que las entradas están
					indice = 1
					#print("ANTERIOR")						#en UNO por defecto. O sea, usa lógica negativa
					break									#
			elif(not(GPIO.input(SIGUIENTE))):				#
				if(no_rebote(SIGUIENTE)):					#
					NEXT = True								#Los break son para que si se presiona más de un botón a la vez, se tome en cuenta
	#				print("NEXT")							#solo el primero que se apretó
					indice = 2
					break									#
			elif(not(GPIO.input(PARAR))):					#
				if(no_rebote(PARAR)):						#
					STOP = True								#
	#				print("STOP")							#
					indice = 3
					break									#
			elif(not(GPIO.input(SUBIR_VOLUMEN))):			#
				if(no_rebote(SUBIR_VOLUMEN)):				#
					VOL_UP = True							#
	#				print("VOL UP")							#
					indice = 4
					break									#
			elif(not(GPIO.input(BAJAR_VOLUMEN))):			#
				if(no_rebote(BAJAR_VOLUMEN)):				#
					VOL_DOWN = True							#
	#				print("VOL DOWN")						#
					indice = 5
					break									#
			elif(not(GPIO.input(CAMBIAR_CROSSFADE))):		#
				if(no_rebote(CAMBIAR_CROSSFADE)):			#
					TOGGLE_CROSSFADE = True					#
	#				print("crossfade")						#
					indice = 6
					break									#
			elif(not(GPIO.input(CAMBIAR_RANDOM))):			#
				if(no_rebote(CAMBIAR_RANDOM)):				#
					TOGGLE_RANDOM = True					#
	#				print("cambiar random")					#
					indice = 7
					break									#


			end=time.time()									#Como acá va a pasar la mayor parte del tiempo, es lógico que esto se imprima acá
			if (end - start > TIEMPO_REFRESCO_LCD):			#....se imprima o se extraigan estos datos
				start=time.time()							#
				estado_player=os.popen('mpc').read()		#
				os.system("clear")							#
				print(estado_player)						#



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
			HAY_ALGO_PARA_EJECUTAR = True


		if HAY_ALGO_PARA_EJECUTAR:					#
			if(PLAY_PAUSE):							# Si hay algo para ejecutar, entro acá, ejecuto y bajo todas las banderas
				os.system("mpc " + estado[indice] +" "+ str(song))	#
				#os.system("mpc toggle")  TENGO QUE VER ACÁ DE HACER QUE LA PRIMERA VEZ QUE ENTRA VAYA A UNA CANCIÓN ALEATORIA Y dps FUNCIONE COMO PLAY/PAUSE
			if(PREV):
				os.system("mpc " + estado[indice])
			if(NEXT):								#
				os.system("mpc " + estado[indice])	#
			if(STOP):								#
				os.system("mpc " + estado[indice])	#
			if(VOL_UP):								#
				os.system("mpc " + estado[indice])	#
			if(VOL_DOWN):							#
				os.system("mpc " + estado[indice])	#
			if(TOGGLE_CROSSFADE):					#
				os.system("mpc " + estado[indice])	#
			if(TOGGLE_RANDOM):						#
				os.system("mpc " + estado[indice])	#
													#
			HAY_ALGO_PARA_EJECUTAR = False			#
			PLAY_PAUSE = PREV = NEXT = STOP = VOL_UP = VOL_DOWN = TOGGLE_CROSSFADE = TOGGLE_RANDOM = False
			ALGUN_BOTON_APRETADO = False

#--------------------------------------------------------------------------------------------
#								Fin del programa principal								    #
#____________________________________________________________________________________________

################################################################################################
#											FUNCIONES										   #
################################################################################################
def no_rebote(boton):					#Antirrebotes.
	boton_antes = GPIO.input(boton)		#Recibe el número del gpio (el botón) presionado
	time.sleep(TIEMPO_ANTIRREBOTES)		#elimina rebotes y si está todo OK, levanta la 
	boton_despues = GPIO.input(boton)	#bandera avisando que hay algún botón apretado
										#
	if(boton_antes == boton_despues):	#
		global ALGUN_BOTON_APRETADO		#
		ALGUN_BOTON_APRETADO = True		#
#		print("BOTON APRETADO")			#
		return True						#
	else:								#
#		print("FALSA ALARMA")			#
		return False					#


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		pass
		# lcd_byte(0x01, LCD_CMD)
		# lcd_string("Goodbye!", LCD_LINE_1)
		# GPIO.cleanup()