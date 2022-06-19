import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

RED = 19
GREEN = 35
BLUE = 37
GPIO.setup(RED, GPIO.OUT)
rojo = GPIO.PWM(RED, 100)
GPIO.setup(GREEN, GPIO.OUT)
verde = GPIO.PWM(GREEN, 100)
GPIO.setup(BLUE, GPIO.OUT)
azul = GPIO.PWM(BLUE, 100)
time.sleep(10)
print("esperando...")
rojo.start(0)   
verde.start(0) 
azul.start(0) 
time.sleep(10)
print("esperando...") 

while True:
    for i in range(100,-1,-1):
        rojo.ChangeDutyCycle(100 - i)
        time.sleep(0.02)   
    time.sleep(3)
    for i in range(100,-1,-1):
        verde.ChangeDutyCycle(100 - i)
        time.sleep(0.02) 
    time.sleep(3)  
    for i in range(100,-1,-1):
        azul.ChangeDutyCycle(100 - i)
        time.sleep(0.02)    
    time.sleep(3)       

    print("Ciclo completo")