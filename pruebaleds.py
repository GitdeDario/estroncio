import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(24, GPIO.OUTPUT)
rojo = GPIO.PWM(19, 100)
rojo.start(100)    

while True:
    for i in range(100,-1,-1):
        rojo.ChangeDutyCycle(100 - i)
        time.sleep(0.02)           

    print("Ciclo completo")