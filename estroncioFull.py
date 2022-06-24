#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-

import os, random, time, re
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
#---------------------------------------------------------------------------------------------------------------
os.system("clear") #ESTO ES SOLO PARA LIMPIAR LA PANTALLA DURANTE LAS PRUEBAS Y QUE SE VEA BIEN LO QUE IMPRIME. 
		   #SE BORRARÍA EN EL PROGRAMA DE PRODUCCIÓN.
#---------------------------------------------------------------------------------------------------------------
os.system("mpc clear") #Borro todo 
os.system("cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas") #Me paro en el dir donde están las canciones
os.system("mpc add /") #y vuelvo a cargar por si hay nuevas canciones
os.system("mpc crossfade 2") # Arranca con cossfade habilitado dos segundos  
#Extraigo la cantidad de canciones que hay en la lista. En realidad cuenta la cantidad de archivos que hay en ese dir.Lo devuelve como un str y al parecer
#hay un archivo más, así que hay que castear a int y restarle 1.
largoListaCanciones_STR = os.popen('cd /mnt/MPD/USB/sda1-usb-Philips_USB_Flas/; ls -1 | wc -l') 
largoListaCanciones=((int((largoListaCanciones_STR.read()))))-1

#*********************************************************************************************
#		DEFINO CONSTANTES y VARIABLES
#**********************************************************************************************
# Definición de constantes usadas en el LCD
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Constantes de tiempo usadas en el LCD
E_PULSE = 0.0005
E_DELAY = 0.0005

#Otras constantes
TIEMPO_ANTIRREBOTES = 0.020	#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1		#1 segundo para que recargar datos de la pista que se está reproduciendo
TIEMPO_ESPERA_ENCODER = 10	# Espera antes de salir del loop de esperar a que se actue sobre el encoder o se de enter en el encoder
#Variables para la máquina de estado
Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = False	#Estados para la máquina de estados del encoder
FINErf = FINEif = True


#*********************************************************************************************
#		DEFINO LOS GPIO
#**********************************************************************************************

# GPIO usados por los pulsadores
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

PAUSA = 40
GPIO.setup(PAUSA, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_CROSSFADE = 19
GPIO.setup(CAMBIAR_CROSSFADE, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CAMBIAR_RANDOM = 21
GPIO.setup(CAMBIAR_RANDOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)	


# GPIO usados por el ENCODER
CLK = 23
GPIO.setup(CLK, GPIO.IN)	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene
DT = 29
GPIO.setup(DT, GPIO.IN)		#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene
PULSADOR_ENCODER = 31 
GPIO.setup(PULSADOR_ENCODER, GPIO.IN) 	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

# GPIO usados por el LCD
LCD_RS = 12
GPIO.setup(LCD_RS, GPIO.OUT) # RS
LCD_E  = 16
GPIO.setup(LCD_E, GPIO.OUT)
LCD_D4 = 18
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
LCD_D5 = 22
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
LCD_D6 = 24
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
LCD_D7 = 26
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

# GPIO usados para el transistor que controla el motor
MOTOR = 33
GPIO.setup(MOTOR, GPIO.OUT)
GPIO.output(MOTOR, False)	# motor arranca apagado

#GPIO usados para led RGB
ROJO = 40
GPIO.setup(ROJO, GPIO.OUT)
GPIO.output(ROJO, True)		# Arrancamos con el led apagado. True lo apaga porque los leds trabajan con lógica negativa. Son de ánodo común

VERDE = 35
GPIO.setup(VERDE, GPIO.OUT)
GPIO.output(VERDE, True)		# Arrancamos con el led apagado. True lo apaga porque los leds trabajan con lógica negativa. Son de ánodo común

AZUL = 37
GPIO.setup(AZUL, GPIO.OUT)
GPIO.output(AZUL, True)		# Arrancamos con el led apagado. True lo apaga porque los leds trabajan con lógica negativa. Son de ánodo común
 

#--------------------------------------------------------------------------------------------
#		FIN DEFINICIÓN DE LOS GPIO
#--------------------------------------------------------------------------------------------

#***********************************************************************************************
#	DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random", "pause"]
indice = 0

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():

	#Variable para el estado del pulsador del encoder
	ENTER_ENCODER = False
	lcd_init()
	start = time.time()
	song = random.randint(1, largoListaCanciones)
	os.system("mpc play" +" "+ str(song)) ###################BORRAR ESTO!!!!!!!!!!!!!!!!!!!!!!!!!
	desde = 0	# para mostrar cadena de texto en el LCD

	while(True):
		
		if actuo_el_encoder():				 
			lcd_string(estado[indice], LCD_LINE_1) 				#acá que imprima lo que se está seleccionando en el LCD, siga leyendo el encoder
			lcd_string(" Presione ENTER", LCD_LINE_2) 			#y avise que hay que dar enter y se quede
			ENTER_ENCODER = esperar_enter_encoder() 	#esperando a que aprete enter. cuando da enter, sigo....
					

		if se_pulso_un_boton() or ENTER_ENCODER:	
			espero_a_que_se_libere_el_pulsador()
			os.system("mpc"+" "+estado[indice])		#
			ENTER_ENCODER = False

		ENTER_ENCODER = not(GPIO.input(PULSADOR_ENCODER))
		if ENTER_ENCODER:	
			espero_a_que_se_libere_el_pulsador()
			os.system("mpc"+" "+estado[indice])		#
			ENTER_ENCODER = False

		if (estado[indice] == "stop"):
			STATE = estado[indice]
		
		if (estado[indice] == "play"):
			STATE = estado[indice]

		if (estado[indice] == "pause"):
			STATE = estado[indice]
		

		if (STATE == "stop"):					# Si el edo es stop, muestro eso en el display porque si intennto ejecutar la funcion
			lcd_string("      STOP      ", LCD_LINE_1)	# info_reproduciendo(), da un error al no poder leer cosas que no se muestran si está en stop
			lcd_string("",LCD_LINE_2)
			GPIO.output(MOTOR, False)
			GPIO.output(ROJO, False)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común
			GPIO.output(VERDE, True)
			GPIO.output(AZUL, True)

		if (STATE == "play"):
			GPIO.output(MOTOR, True)
			GPIO.output(ROJO, False)
			GPIO.output(VERDE, True)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común
			GPIO.output(AZUL, True)

		if (STATE == "pause"):
			lcd_string("      PAUSE     ", LCD_LINE_1)	# info_reproduciendo(), da un error al no poder leer cosas que no se muestran si está en stop
			lcd_string("",LCD_LINE_2)
			GPIO.output(MOTOR, False)
			GPIO.output(ROJO, True)
			GPIO.output(VERDE, True)
			GPIO.output(AZUL, False)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común

		if (STATE != "stop" and STATE != "pause"):											# si NO estoy en stop:
			end = time.time()							# Como acá va a pasar la mayor parte del tiempo, es lógico que esto se imprima acá
			if (end - start > TIEMPO_REFRESCO_LCD):		# ....se imprima o se extraigan estos datos
				start = time.time()						#
				(volumen, tema, tiempo, tiempo_total) = info_reproduciendo()
				lcd_string(tema[desde:]+"  *  "+tema[:desde], LCD_LINE_1)		# Envio el texto al LCD de forma tal que se muestra
				if (desde < len(tema) and tiempo_total != "100%"):				# circularmente el tema
					desde += 1													#
				else:															#
					desde = 0													#
																				#
				lcd_string("vol:"+volumen + "%" + "  " + tiempo, LCD_LINE_2)	# Y tambien envio info del volumen y el tiempo transcurrido de reproduccion
			
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

def se_pulso_un_boton():
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

def actuo_el_encoder():
	global Ei
	global Er1 
	global Er2
	global Erf
	global Ei1
	global Ei2
	global Eif
	global FINErf 
	global FINEif
	global indice

	clk_actual = GPIO.input(CLK)
	dt_actual = GPIO.input(DT)

	ACTUO_EL_ENCODER = False

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
		ACTUO_EL_ENCODER = True
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
		ACTUO_EL_ENCODER = True
		if(indice > 0):
			indice -= 1
		else:
			indice = len(estado)-1
			
	return ACTUO_EL_ENCODER


def espero_a_que_se_libere_el_pulsador():
	ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
					or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
					or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
					or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
					or not(GPIO.input(SUBIR_VOLUMEN)) 					#
					or not(GPIO.input(BAJAR_VOLUMEN)) 					#
					or not(GPIO.input(CAMBIAR_CROSSFADE))				#
					or not(GPIO.input(CAMBIAR_RANDOM)) 					#
					or not(GPIO.input(PULSADOR_ENCODER))
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
					or not(GPIO.input(PULSADOR_ENCODER))
					)


def esperar_enter_encoder():
	start_timer = time.time()
	ENTER_ENCODER = not(GPIO.input(PULSADOR_ENCODER))	#
	while not ENTER_ENCODER:								#	
		ENTER_ENCODER = not(GPIO.input(PULSADOR_ENCODER))	#	
		if actuo_el_encoder():									#	
			lcd_string(estado[indice], LCD_LINE_1)				#
		stop_timer = time.time()
		if stop_timer - start_timer >= TIEMPO_ESPERA_ENCODER:
			break																
	lcd_string("       OK", LCD_LINE_1)						#
	lcd_string("", LCD_LINE_2)								#
	time.sleep(1)
	return ENTER_ENCODER


def info_reproduciendo():
	estado_player = os.popen('mpc').read()		#Extraigo los datos del estado del reproductor
			
	volRegex = re.compile(r'volume:( ){0,2}(\d){1,3}')	#Extraigo la info del vol. Se que es lo que empieza con "volumen",
	volumenRaw = volRegex.search(estado_player)			# hay de 0 a 2 espacios y  le siguen de 1 a 3 digitos
	volumen = str(volumenRaw.group())[-3:]				#Me quedo con los ultimos 3 lugares y lo convierto a string

	temaRegex = re.compile(r'Flas/(.*?)mp3')			#Idem con el titulo de la cancion e interprete(s)
	temaRaw = temaRegex.search(estado_player)			#
	tema_i = str(temaRaw.group())[5:]					#Elimino el "Flas/" del inicio
	tema= tema_i[:-4]									#Elimino el "mp3" del final y solo queda CANTANTE - TITULO DEL TEMA

	tiempoRegex = re.compile(r'(\d)+:(\d)+')
	tiempoRaw = tiempoRegex.search(estado_player)
	tiempo = str(tiempoRaw.group())

	tiempo_totalRegex = re.compile(r'((\d){1,3}%)')				# Esto es el porcentaje de avance. Es para refrescar el LCD 
	tiempo_totalRaw = tiempo_totalRegex.search(estado_player)	# cuando se alcanza el 100% y que lo que se muesra arranque desde
	tiempo_total = str(tiempo_totalRaw.group())[-3:]			# el principio: INTERPRETE - TEMA	

	return (volumen, tema, tiempo, tiempo_total)


def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

	GPIO.output(LCD_RS, mode) # RS

  # High bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x10==0x10:
		GPIO.output(LCD_D4, True)
	if bits&0x20==0x20:
		GPIO.output(LCD_D5, True)
	if bits&0x40==0x40:
		GPIO.output(LCD_D6, True)
	if bits&0x80==0x80:
		GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
	lcd_toggle_enable()

  # Low bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x01==0x01:
		GPIO.output(LCD_D4, True)
	if bits&0x02==0x02:
		GPIO.output(LCD_D5, True)
	if bits&0x04==0x04:
		GPIO.output(LCD_D6, True)
	if bits&0x08==0x08:
		GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
	lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display
	message = message.ljust(LCD_WIDTH," ")
	lcd_byte(line, LCD_CMD)
	for i in range(LCD_WIDTH):
		lcd_byte(ord(message[i]),LCD_CHR)

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		lcd_byte(0x01, LCD_CMD)
		lcd_string("Goodbye!",LCD_LINE_1)
		GPIO.cleanup()
