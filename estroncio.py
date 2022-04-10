#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-

import os, random, time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
#---------------------------------------------------------------------------------------------------------------
os.system("clear") #ESTO ES SOLO PARA LIMPIAR LA PANTALLA DURANTE LAS PRUEBAS Y QUE SE VEA BIEN LO QUE IMPRIME. 
#---------------------------------------------------------------------------------------------------------------
os.system("mpc clear") 									#Borro todo 
os.system("cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas") 	#Me paro en el dir donde están las canciones
os.system("mpc add /") 									#y vuelvo a cargar por si hay nuevas canciones
os.system("mpc crossfade") 								# Arranca con cossfade habilitado desgundos  
#Extraigo la cantidad de canciones que hay en la lista. En realidad cuenta la cantidad de archivos que hay en ese dir.Lo devuelve como un str y al parecer
#hay un archivo más, así que hay que castear a int y restarle 1.
largoListaCanciones_STR = os.popen('cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas/; ls -1 | wc -l') 
largoListaCanciones=((int((largoListaCanciones_STR.read()))))-1

#*********************************************************************************************
#										DEFINO LOS GPIO
#**********************************************************************************************
REPRODUCIR_PAUSA = 7
GPIO.setup(REPRODUCIR_PAUSA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ANTERIOR = 11
GPIO.setup(ANTERIOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SIGUIENTE = 12
GPIO.setup(SIGUIENTE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PARAR = 13
GPIO.setup(PARAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SUBIR_VOLUMEN = 15
GPIO.setup(SUBIR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BAJAR_VOLUMEN = 16
GPIO.setup(BAJAR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_CROSSFADE = 18
GPIO.setup(CAMBIAR_CROSSFADE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_RANDOM = 22
GPIO.setup(CAMBIAR_RANDOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CLK = 36
GPIO.setup(CLK, GPIO.IN)	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

DT = 38
GPIO.setup(DT, GPIO.IN)		#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

SW = 40 
GPIO.setup(SW, GPIO.IN) 	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

#--------------------------------------------------------------------------------------------
#		FIN DEFINICIÓN DE LOS GPIO
#--------------------------------------------------------------------------------------------

#***********************************************************************************************
#	DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0
BOTON_OK_LIBRE = True
Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = False
FINErf = FINEif = True
HAY_ALGO_PARA_EJECUTAR = False
ALGUN_BOTON_APRETADO = False
TIEMPO_ANTIRREBOTES = 0.020		#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1			#1 segundo para que recargar datos de la pista que se está reproduciendo

################################################################################################
#											FUNCIONES										   #
################################################################################################
def sin_rebote(boton):					#Antirrebotes.
	global ALGUN_BOTON_APRETADO		#
	boton_antes = GPIO.input(boton)		#Recibe el número del gpio (el botón) presionado
	time.sleep(TIEMPO_ANTIRREBOTES)		#elimina rebotes y si está todo OK, levanta la 
	boton_despues = GPIO.input(boton)	#bandera avisando que hay algún botón apretado
										#
	if(boton_antes == boton_despues):	#
		ALGUN_BOTON_APRETADO = True		#
		return True						#
	else:								#
		return False					#

	print(ALGUN_BOTON_APRETADO)
	time.sleep(2)
	

def leer_encoder():
	clk_actual = GPIO.input(CLK)
	dt_actual = GPIO.input(DT)
	global indice
	global Ei, Er1, Er2, Erf,  Ei1, Ei2, Eif, FINErf,  FINEif

	if ((FINErf or FINEif) and (clk_actual == 1) and (dt_actual ==1)):
		Ei = True
		Er1 = Er2 = Erf = FINErf = Ei1 = Ei2 = Eif = FINEif = False
		
	if(Ei and (clk_actual == 0) and (dt_actual ==1)):
		Er1 = True
		Ei = Er2 = Erf = FINErf = Ei1 = Ei2 = Eif = FINEif = False
	if(Er1 and (clk_actual == 0) and (dt_actual ==0)):
		Er2 = True
		Ei = Er1 = Erf = FINErf = Ei1 = Ei2 = Eif = FINEif = False
	if(Er2 and (clk_actual == 1) and (dt_actual ==1)):
		Erf = True
		Ei = Er1 = Er2 = FINErf = Ei1 = Ei2 = Eif = FINEif = False
	if(Erf and (clk_actual == 1) and (dt_actual ==1)):
		FINErf = True
		Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = FINEif = False
		if(indice < len(estado)-1):
			indice += 1
		else:
			indice = 0

	if(Ei and (clk_actual == 1) and (dt_actual ==0)):
		Ei1 = True
		Ei = Er1 = Er2 = Erf = FINErf = Ei2 = Eif = FINEif = False
	if(Ei1 and (clk_actual == 0) and (dt_actual ==0)):
		Ei2 = True
		Ei = Er1 = Er2 = Erf = FINErf = Ei1 = Eif = FINEif = False
	if(Ei2 and (clk_actual == 0) and (dt_actual ==1)):
		Eif = True
		Ei = Er1 = Er2 = Erf = FINErf = Ei1 = Ei2 = FINEif = False
	if(Eif and (clk_actual == 1) and (dt_actual ==1)):
		FINEif = True
		Ei = Er1 = Er2 = Erf = FINErf = Ei1 = Ei2 = Eif = False
		if(indice > 0):
			indice -= 1
		else:
			indice = len(estado)-1


def leer_pulsadores():
	global indice

	if(not(GPIO.input(REPRODUCIR_PAUSA))):			#
		if(sin_rebote(REPRODUCIR_PAUSA)):			#En cuanto algún botón se presiona, se elimino la posibilidad de que sea un rebote
			indice = 0								#con la función antirrebotes. Si no es un rebote, en la función mismo se levanta una
												#
	elif(not(GPIO.input(ANTERIOR))):				#bandera para avisar que hay un botón apretado y se discrimina cuál es el botón presionado.
		if(sin_rebote(ANTERIOR)):					#Los "NOT" son porque hay resistencias de pull up internas, por lo que las entradas están
			indice = 1								#en UNO por defecto. O sea, usa lógica negativa
												#
	elif(not(GPIO.input(SIGUIENTE))):				#
		if(sin_rebote(SIGUIENTE)):					#
			indice = 2
												#
	elif(not(GPIO.input(PARAR))):					#
		if(sin_rebote(PARAR)):						#
			indice = 3
												#
	elif(not(GPIO.input(SUBIR_VOLUMEN))):			#
		if(sin_rebote(SUBIR_VOLUMEN)):				#
			indice = 4
												#
	elif(not(GPIO.input(BAJAR_VOLUMEN))):			#
		if(sin_rebote(BAJAR_VOLUMEN)):				#
			indice = 5
												#
	elif(not(GPIO.input(CAMBIAR_CROSSFADE))):		#
		if(sin_rebote(CAMBIAR_CROSSFADE)):			#
			indice = 6
												#
	elif(not(GPIO.input(CAMBIAR_RANDOM))):			#
		if(sin_rebote(CAMBIAR_RANDOM)):				#
			indice = 7
												#

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

print("Iniciando estroncio...")
start = time.time()

while(True):

	while(not ALGUN_BOTON_APRETADO or BOTON_OK_LIBRE):	#Mientras no haya ningún botón apretado, me quedo leyendo lanentrada
		BOTON_OK_LIBRE = GPIO.input(SW)

		if(not(BOTON_OK_LIBRE)):
			if(sin_rebote(SW)):
				BOTON_OK_LIBRE = False
			else:
				BOTON_OK_LIBRE = True

		leer_encoder()
		leer_pulsadores()
		
		end=time.time()									#Como acá va a pasar la mayor parte del tiempo, es lógico que esto se imprima acá
		if (end - start > TIEMPO_REFRESCO_LCD):			#....se imprima o se extraigan estos datos
			start=time.time()							#
			estado_player=os.popen('mpc').read()		#
			os.system("clear")							#
			print(estado_player)						#
			print(str(estado[indice]).upper())

	while(not BOTON_OK_LIBRE):										# Si el botón del enconder se mantiene presionado, me quedo acá.
		BOTON_OK_LIBRE = GPIO.input(SW)								# Sigo leyendo la entrada del pulsador y levanto la bandera para avisar
		HAY_ALGO_PARA_EJECUTAR = True								# que hay algo para ejecutar.

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
		os.system("mpc " + estado[indice])		# Si hay algo para ejecutar, ejecuto.
		HAY_ALGO_PARA_EJECUTAR = False

#--------------------------------------------------------------------------------------------
#								Fin del programa principal								    #
#____________________________________________________________________________________________
