# https://www.aranacorp.com/es/controla-un-stepper-con-raspberrypi/

#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO

# Usa el modo BOARD para los GPIO
GPIO.setmode(GPIO.BOARD)

# Define GPIO signals to use Pins GPIO24,GPIO25,GPIO8,GPIO7
StepPins = [8,10,32,34]
# Todos los pines como saldas
for pin in StepPins:
	GPIO.setup(pin,GPIO.OUT)
	GPIO.output(pin, False)
# Espera luego de setear cosas
WaitTime = 0.005

# Secuencia de paso simples. Máximo par pero más conusmo
StepCount1 = 4
Seq1 = []
Seq1 = [i for i in range(0, StepCount1)]
Seq1[0] = [1,0,0,0]
Seq1[1] = [0,1,0,0]
Seq1[2] = [0,0,1,0]
Seq1[3] = [0,0,0,1]

# Secuencia de paso media. Menos par y menos consumo
StepCount2 = 8
Seq2 = []
Seq2 = [i for i in range(0, StepCount2)]
Seq2[0] = [1,0,0,0]
Seq2[1] = [1,1,0,0]
Seq2[2] = [0,1,0,0]
Seq2[3] = [0,1,1,0]
Seq2[4] = [0,0,1,0]
Seq2[5] = [0,0,1,1]
Seq2[6] = [0,0,0,1]
Seq2[7] = [1,0,0,1]

# Se selecciona una secuencia para usar. Se elige la de paso medio
Seq = Seq2
StepCount = StepCount2

def steps(nb):
	StepCounter = 0
	if( nb < 0): 
		sign = -1
	else: 
		sign = 1
	nb = sign*nb*2 # Multiplica por dos porque usa la secuencia de pasos media
	print("nbsteps {} and sign {}".format(nb,sign))
	for i in range(nb):
		for pin in range(4):
			xpin = StepPins[pin]
			if(Seq[StepCounter][pin] != 0):
				GPIO.output(xpin, True)
			else:
				GPIO.output(xpin, False)
		StepCounter += sign
# Si se alcanza el final de todos los pasos que teiene las secuencia, arrancamos de nuevo
		if (StepCounter == StepCount):
			StepCounter = 0
		if (StepCounter < 0):
			StepCounter = StepCount-1
		# Wait before moving on
		time.sleep(WaitTime)

# Main loop
nbStepsPerRev = 2048
if __name__ == '__main__' :
	hasRun=False
	while not hasRun:
		steps(nbStepsPerRev)    # Ejecuta una vuelta en sentido horario
		time.sleep(1)
		steps(-nbStepsPerRev)   # Ejecuta una vuelta en sentido antihorario
		time.sleep(1)

		hasRun=True

	print("Stop motor")
	for pin in StepPins:
		GPIO.output(pin, False)