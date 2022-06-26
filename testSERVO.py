import RPi.GPIO as GPIO
import time

servoPIN = 38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) 
try:
  while True:
    p.ChangeDutyCycle(60)
    time.sleep(1)
    p.ChangeDutyCycle(2.5)
    time.sleep(1)
    # p.ChangeDutyCycle(2)
    # time.sleep(1)
    # p.ChangeDutyCycle(12.5)
    # time.sleep(1)
    # p.ChangeDutyCycle(10)
    # time.sleep(1)
    # p.ChangeDutyCycle(7.5)
    # time.sleep(1)
    # p.ChangeDutyCycle(5)
    # time.sleep(1)
    # p.ChangeDutyCycle(2.5)
    # time.sleep(1)
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()