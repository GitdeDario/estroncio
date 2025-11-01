import RPi.GPIO as GPIO

#*********************************************************************************************
#		DEFINO LOS GPIO
#**********************************************************************************************

# GPIO usados por los pulsadores
PLAY = 3	# Play y Next (Tiene doble funcionalidad. Si está en play es next y si no, es play)
GPIO.setup(PLAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ANTERIOR = 5 # Prev
GPIO.setup(ANTERIOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

TOPE_PUERTA_CERRADA = 7
GPIO.setup(TOPE_PUERTA_CERRADA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

TOPE_PUERTA_ABIERTA = 21
GPIO.setup(TOPE_PUERTA_ABIERTA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

PARAR = 11	# Stop
GPIO.setup(PARAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SUBIR_VOLUMEN = 13
GPIO.setup(SUBIR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BAJAR_VOLUMEN = 15
GPIO.setup(BAJAR_VOLUMEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PAUSA = 36	# Pause
GPIO.setup(PAUSA, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# GPIO usados por el ENCODER
CLK = 23
GPIO.setup(CLK, GPIO.IN)	# No necesita pull up interna en la raspi porque el módulo de encoder ya tiene
DT = 29
GPIO.setup(DT, GPIO.IN)		# No necesita pull up interna en la raspi porque el módulo de encoder ya tiene
PULSADOR_ENCODER = 31 
GPIO.setup(PULSADOR_ENCODER, GPIO.IN) 	# No necesita pull up interna en la raspi porque el módulo de encoder ya tiene

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

LCD_ON = 19
GPIO.setup(LCD_ON, GPIO.OUT)
GPIO.output(LCD_ON, True)		# Arrancamos con retroiluminación del LCD prendido

# GPIO usados para el transistor que controla el motor
MOTOR = 33
GPIO.setup(MOTOR, GPIO.OUT)
GPIO.output(MOTOR, False)	# motor arranca apagado

# GPIO usados en el stepper que abre/cierra la tapa
StepperPins = [8,10,32,38]
# Y los ponemos todos como salids
for pin in StepperPins:
	GPIO.setup(pin,GPIO.OUT)
	GPIO.output(pin, False)

# GPIO usados para led RGB
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