import RPi.GPIO as GPIO

k_led = 23
y_led = 24
buzzer = 4
kapi = 17

GPIO.setmode(GPIO.BCM)

GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(k_led, GPIO.OUT)
GPIO.setup(y_led, GPIO.OUT)
GPIO.setup(kapi, GPIO.OUT)

GPIO.output(k_led, False)
GPIO.output(y_led, False)
GPIO.output(buzzer, False)
GPIO.output(kapi, False)
