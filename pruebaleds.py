from re import U
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
print("esperando...")
time.sleep(3)

rojo.start(100)   
verde.start(100) 
azul.start(100) 
print("esperando...")
time.sleep(3)
 

while True:
    rojo.ChangeDutyCycle(100)
    verde.ChangeDutyCycle(0)
    azul.ChangeDutyCycle(0)
    # for i in range(100,-1,-1):
    #     rojo.ChangeDutyCycle(100 - i)
    #     time.sleep(0.02)  
    # rojo.ChangeDutyCycle(0) 
    # time.sleep(3)
    # for i in range(100,-1,-1):
    #     verde.ChangeDutyCycle(100 - i)
    #     time.sleep(0.02) 
    # verde.ChangeDutyCycle(0)
    # time.sleep(3)  
    # for i in range(100,-1,-1):
    #     azul.ChangeDutyCycle(100 - i)
    #     time.sleep(0.02) 
    # azul.ChangeDutyCycle(0)   
    # time.sleep(3)       

    print("Ciclo completo")