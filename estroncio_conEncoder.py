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

CLK = 23
GPIO.setup(CLK, GPIO.IN)	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

DT = 29
GPIO.setup(DT, GPIO.IN)		#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

SW = 31 
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)	#Este SÍ necesita porque el pulsador del encoder NO tiene resistencia


#--------------------------------------------------------------------------------------------
#		FIN DEFINICIÓN DE LOS GPIO
#--------------------------------------------------------------------------------------------

#***********************************************************************************************
#	DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
# Estas van en inglés para no entreverarlas con las def de GPIO que se llaman "igual"
#************************************************************************************************
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0
BOTON_OK_LIBRE = True
ESTADO_CLK_ANTERIOR = GPIO.input(CLK)
indice = 0
TIEMPO_ANTIRREBOTES = 0.020	#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1		#1 segundo para que recargar datos de la pista que se está reproduciendo

Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = False
FINErf = FINEif = True
################################################################################################
#				FUNCIONES
################################################################################################
def sin_rebotes(boton):			#Antirrebotes.
	boton_antes = GPIO.input(boton)		#Recibe el número del gpio (el botón) presionado
	time.sleep(TIEMPO_ANTIRREBOTES)		#elimina rebotes y si está todo OK, levanta la 
	boton_despues = GPIO.input(boton)	#bandera avisando que hay algún botón apretado
						#
	if(boton_antes == boton_despues):	#
		print("BOTON APRETADO y SIN REBOTES")		#
		return True			#
	else:					#
		print("REBOTE. FALSA ALARMA")	#
		return False			#

def encoder():
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
			print(estado[indice])

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
			print(estado[indice])

			
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#				Inicio del programa principal				    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

print("Se inicia el programa........")
start = time.time()
song = random.randint(1,largoListaCanciones)
os.system("mpc play") ###################BORRAR ESTO!!!!!!!!!!!!!!!!!!!!!!!!!

while(1==1):
	while(BOTON_OK_LIBRE):
		clk_actual = GPIO.input(CLK)
		dt_actual = GPIO.input(DT)
		BOTON_OK_LIBRE = GPIO.input(SW)

		if(not(BOTON_OK_LIBRE)):
			if(sin_rebotes(SW)):
				BOTON_OK_LIBRE = False
			else:
				BOTON_OK_LIBRE = True

		encoder()


		end=time.time()
		if(end - start > TIEMPO_REFRESCO_LCD):
			start = time.time()
			estado_player = os.popen('mpc').read()
			os.system("clear")
			print(estado_player)
			print(estado[indice])





	while(not BOTON_OK_LIBRE):
		BOTON_OK_LIBRE = GPIO.input(SW)
		HAY_ALGO_PARA_EJECUTAR = True

	if HAY_ALGO_PARA_EJECUTAR:					#
		os.system("mpc " + estado[indice])
			#os.system("mpc toggle")  TENGO QUE VER ACÁ DE HACER QUE LA PRIMERA VEZ QUE ENTRA VAYA A UNA CANCIÓN ALEATORIA Y dps FUNCIONE COMO PLAY/PAUSE

		HAY_ALGO_PARA_EJECUTAR = False
		BOTON_OK_LIBRE = True

#--------------------------------------------------------------------------------------------
#				Fin del programa principal				    #
#____________________________________________________________________________________________
