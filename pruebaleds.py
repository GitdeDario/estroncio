import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(19, GPIO.OUT)
rojo = GPIO.PWM(19, 100)
rojo.start(0)   
time.sleep(3) 

while True:
    for i in range(100,-1,-1):
        rojo.ChangeDutyCycle(100 - i)
        time.sleep(0.02)           

    print("Ciclo completo")