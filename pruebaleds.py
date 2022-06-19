from leds_RGB import *

def main():
    try:
        GPIO.setmode(GPIO.BOARD)
        for i in pins:
            GPIO.setup(pins[i], GPIO.OUT, initial=GPIO.HIGH)

        led = Led(pins['Red'], pins['Green'], pins['Blue'])

        while True:
            for nombre, color in COLORS.items():
                print('Color: {0}'.format(nombre))
                led.set_color(color)
                time.sleep(2)
                reset()
                # led.set_color(0x000000)
        led.stop()
        GPIO.output(pins, GPIO.HIGH)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()