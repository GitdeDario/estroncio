#Esto para que reconozca tildes y caracteres por el estilo:
# -*- coding: utf-8 -*-
import os, random, time, re
import RPi.GPIO as GPIO
from PINES import *
from ctesYvariables import *
from funciones import *
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


inicializacion()
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#								Inicio del programa principal							    #
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def main():
	abrir_tapa()
	#Variable para el estado del pulsador del encoder
	ENTER_ENCODER = False
	global indice
	global no_estaba_seteado_el_stop
	global no_estaba_seteado_el_pause
	lcd_init()
	start = time.time()
	#song = random.randint(1, largoListaCanciones)
	#os.system("mpc play" +" "+ str(song)) ###################BORRAR ESTO!!!!!!!!!!!!!!!!!!!!!!!!!
	os.system("mpc stop")	# Arrancamos en stop
	desde = 0	# para mostrar cadena de texto en el LCD
	
	while(True):
     		
		if actuo_el_encoder():		
			ENTER_ENCODER = esperar_enter_encoder() 	# esperando a que aprete enter. cuando da enter, sigo....
		
		if se_pulso_un_boton() or ENTER_ENCODER:	
			espero_a_que_se_libere_el_pulsador()
			os.system("mpc"+" "+estado[indice])			# 
			ENTER_ENCODER = False

		ENTER_ENCODER = not(GPIO.input(PULSADOR_ENCODER))
		if ENTER_ENCODER:	
			espero_a_que_se_libere_el_pulsador()
			os.system("mpc"+" "+estado[indice])			#
			lcd_string("OK".center(LCD_WIDTH), LCD_LINE_1)						#
			if estado[indice] == "random":
				lcd_string((estado[indice].upper()+": "+info_reproduciendo()[4]).center(LCD_WIDTH), LCD_LINE_2)								#
			else:
				lcd_string(estado[indice].upper().center(LCD_WIDTH), LCD_LINE_2)								#
			time.sleep(1)
			ENTER_ENCODER = False

		if (estado[indice] == "stop"):
			STATE = estado[indice]
		if (estado[indice] == "play"):
			STATE = estado[indice]
		if (estado[indice] == "pause"):
			STATE = estado[indice]

		if (STATE == "stop"): # Si el edo es stop, muestro eso en el display porque si intento ejecutar la funcion info_reproduciendo(), da un error al no poder leer cosas que no se muestran si está en stop
			if no_estaba_seteado_el_stop:
				lcd_string("STOP".center(LCD_WIDTH), LCD_LINE_1)	# 
				lcd_string("",LCD_LINE_2)
				GPIO.output(MOTOR, False)
				GPIO.output(ROJO, False)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común
				GPIO.output(VERDE, True)
				GPIO.output(AZUL, True)
				no_estaba_seteado_el_stop = False
				no_estaba_seteado_el_pause = True

		if (STATE == "play"):
			GPIO.output(MOTOR, True)
			GPIO.output(ROJO, True)
			GPIO.output(VERDE, False)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común
			GPIO.output(AZUL, True)
			no_estaba_seteado_el_stop = True
			no_estaba_seteado_el_pause = True

		if (STATE == "pause"):
			if no_estaba_seteado_el_pause:
				lcd_string("PAUSE".center(LCD_WIDTH), LCD_LINE_1)	# info_reproduciendo(), da un error al no poder leer cosas que no se muestran si está en stop
				lcd_string("",LCD_LINE_2)
				GPIO.output(MOTOR, False)
				GPIO.output(ROJO, True)
				GPIO.output(VERDE, True)
				GPIO.output(AZUL, False)	# False lo prende porque los leds trabajan con lógica negativa. Son de ánodo común
				no_estaba_seteado_el_stop = True
				no_estaba_seteado_el_pause = False

		if (STATE != "stop" and STATE != "pause"):		# si NO estoy en stop:
			end = time.time()							# Como acá va a pasar la mayor parte del tiempo, es lógico que esto se imprima acá
			if (end - start > TIEMPO_REFRESCO_LCD):		# ....se imprima o se extraigan estos datos
				start = time.time()						#
				(volumen, tema, tiempo, tiempo_total, estado_random) = info_reproduciendo()
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



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		lcd_byte(0x01, LCD_CMD)
		lcd_string("Goodbye!".center(LCD_WIDTH),LCD_LINE_1)
		GPIO.cleanup()
