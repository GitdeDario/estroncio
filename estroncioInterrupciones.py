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

CLK = 23
GPIO.setup(CLK, GPIO.IN)	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

DT = 29
GPIO.setup(DT, GPIO.IN)		#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

SW = 31 
GPIO.setup(SW, GPIO.IN) 	#No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

MOTOR = 33
GPIO.setup(MOTOR, GPIO.OUT)
GPIO.output(MOTOR,0)			#El motor arranca apagado

LED_STOP = 35
GPIO.setup(LED_STOP, GPIO.OUT)
GPIO.output(LED_STOP,1)			#El led de stop encendido....porque arranca todo parado



#--------------------------------------------------------------------------------------------
#									FIN DEFINICIÓN DE LOS GPIO
#--------------------------------------------------------------------------------------------

#***********************************************************************************************
#						DEFINO VARIABLES PARA LA MÁQINA DE ESTADOS
#************************************************************************************************

#SI SE AGREGAN FUNCIONES, PONERLAS EN EL FINAL DE ESTA LISTA PARA ASÍ NO AFECTAR EL FUNCIONAMIENTO QUE SE TIENE HASTA EL MOMENTO.
estado = ["play", "prev", "next", "stop", "volume +10", "volume -10", "crossfade", "random"]
indice = 0
BOTON_OK_LIBRE = True	#El pulsador del encoder
Ei = Er1 = Er2 = Erf = Ei1 = Ei2 = Eif = False	#Estados para la máquina de estados del encoder
FINErf = FINEif = True							#Ídem
HAY_ALGO_PARA_EJECUTAR = False	#Bandera
ALGUN_BOTON_APRETADO = False	#Otra bandera para saber si hay un botón apretado y quedarme esperando a que se suelte
TIEMPO_ANTIRREBOTES = 0.020		#20ms para la funcionr "no_rebote"
TIEMPO_REFRESCO_LCD = 1			#1 segundo para que recargar datos de la pista que se está reproduciendo
#--------------------------------------------------------------------------------------------
#					FIN DEFINICIÓN VARIABLES PARA LA MÁQUINA DE ESTADOS
#--------------------------------------------------------------------------------------------


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():
	print("Iniciando estroncio...")
	start = time.time()

	while(True):
		print("runing")
		time.sleep(1)

		# while(not ALGUN_BOTON_APRETADO and BOTON_OK_LIBRE):	#Mientras no haya ningún botón apretado (ni del encoder ni los otros), me quedo leyendo la entrada
		# 	BOTON_OK_LIBRE = GPIO.input(SW)					# Botón del enconder
		# 													#
		# 	if(not(BOTON_OK_LIBRE)):						#
		# 		if(sin_rebote(SW)):							#
		# 			BOTON_OK_LIBRE = False					#
		# 		else:										#
		# 			BOTON_OK_LIBRE = True					#

		# 	leer_encoder()
		# 	leer_pulsadores()
			
		# 	end=time.time()									#Como acá va a pasar la mayor parte del tiempo, es lógico que esto se imprima acá
		# 	if (end - start > TIEMPO_REFRESCO_LCD):			#....se imprima o se extraigan estos datos
		# 		start=time.time()							#
		# 		estado_player=os.popen('mpc').read()		#
		# 		porcentajeRegex = re.compile(r'volume:\d*')
		# 		mo = porcentajeRegex.search(estado_player)
		# 		os.system("clear")							#
		# 		print("**********HHH*****************")
		# 		#mo.group()
		# 		print(mo.group())
		# 		print("***************************")
		# 		print(estado_player)						#
		# 		print(str(estado[indice]).upper())

		# while(not BOTON_OK_LIBRE):										# Si el botón del enconder se mantiene presionado, me quedo acá.
		# 	BOTON_OK_LIBRE = GPIO.input(SW)								# Sigo leyendo la entrada del pulsador y levanto la bandera para avisar
		# 	HAY_ALGO_PARA_EJECUTAR = True								# que hay algo para ejecutar.

		# while(ALGUN_BOTON_APRETADO):									#Si alguno de los otros pulsadores (sin ser el del encoder) está presionado, me quedo acá
		# 	ALGUN_BOTON_APRETADO = (not(GPIO.input(REPRODUCIR_PAUSA)) 	#Me fijo si alguno de los botones está presionado y si lo está, la variable
		# 			or not(GPIO.input(ANTERIOR)) 						#ALGUN_BOTON_APRETADO queda en "1". Los "NOT" son porque los botones tiene pull up's
		# 			or not(GPIO.input(SIGUIENTE)) 						#internos, entonces cuando se presionan, la entrada se pone a tierra ("0"). Así, con
		# 			or not(GPIO.input(PARAR)) 							#los not, cuando se apretan, quedan en "1".
		# 			or not(GPIO.input(SUBIR_VOLUMEN)) 					#
		# 			or not(GPIO.input(BAJAR_VOLUMEN)) 					#
		# 			or not(GPIO.input(CAMBIAR_CROSSFADE))				#
		# 			or not(GPIO.input(CAMBIAR_RANDOM)) 					#
		# 			)
		# 	HAY_ALGO_PARA_EJECUTAR = True


		# if (HAY_ALGO_PARA_EJECUTAR):				#
		# 	os.system("mpc " + estado[indice])		# Si hay algo para ejecutar, ejecuto.

		# 	control_motor()							#En función de si estoy en play o no, prendo o no el motor		
					
		# 	HAY_ALGO_PARA_EJECUTAR = False			#Bajo la bandera

#--------------------------------------------------------------------------------------------
#								Fin del programa principal								    #
#____________________________________________________________________________________________

################################################################################################
#											FUNCIONES										   #
################################################################################################
# def sin_rebote(boton):					#Antirrebotes.
# 	boton_antes = GPIO.input(boton)		#Recibe el número del gpio (el botón) presionado
# 	time.sleep(TIEMPO_ANTIRREBOTES)		#elimina rebotes y si está todo OK, levanta la 
# 	boton_despues = GPIO.input(boton)	#bandera avisando que hay algún botón apretado
# 										#
# 	if(boton_antes == boton_despues):	#
# 		global ALGUN_BOTON_APRETADO		#
# 		ALGUN_BOTON_APRETADO = True		#
# 		return True						#
# 	else:								#
# 		return False					#
	

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


def leer_pulsadores(channel):
	global indice

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

def control_motor():
	if(estado[indice]=="play"):
		GPIO.output(MOTOR,1)				#Si estoy en "play", ENCENDER MOTOR
		GPIO.output(LED_STOP,0)
	if(estado[indice]=="stop"):
		GPIO.output(MOTOR,0)				#Si estoy en "stop", APAGO MOTOR
		GPIO.output(LED_STOP,1)

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

#--------------------------------------------------------------------------------------------
#								FIN DEFINICIÓN DE FUNCIONES
#--------------------------------------------------------------------------------------------

  ################################################################################################
#											INTERRUPCIONES										   #
  ################################################################################################
GPIO.add_event_detect(REPRODUCIR_PAUSA, GPIO.RISSING, callback = leer_pulsadores, bouncetime = 100)
GPIO.add_event_detect(ANTERIOR, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(SIGUIENTE, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(PARAR, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(SUBIR_VOLUMEN, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(BAJAR_VOLUMEN, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(CAMBIAR_CROSSFADE, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
GPIO.add_event_detect(CAMBIAR_RANDOM, GPIO.FALLING, callback = leer_pulsadores, bouncetime = 1000)
#-----------------------------------------------------------------------------------------------
#								FIN DEFINICIÓN DE INTERRUPCIONES
#-----------------------------------------------------------------------------------------------

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		lcd_byte(0x01, LCD_CMD)
		lcd_string("Goodbye!", LCD_LINE_1)
		GPIO.cleanup()