import os 
import sys
import json
import time
import traceback

import RPi.GPIO as GPIO

from helper import *
import helper as h

file_name = os.path.basename(__file__)
	

buzzer_pin = 4 #buzzer_pin = 7  //7. bacak GPIO4
red_led = 23#red_led = 16
green_led = 24#green_led = 18
triger_pin = 17#triger_pin = 11


try:

	def run():
		global buzzer_pin, red_led, green_led, triger_pin
		
		pin_on(buzzer_pin, time_out = 0.1)
		
		pin_on(red_led, time_out = 1)
		time.sleep(1.1)
		
		pin_on(green_led, time_out = 1)
		time.sleep(1.1)
		
		pin_on(triger_pin, time_out = 0.1)
		
		
	#Ana Fonksiyon
	if __name__ == "__main__":	
	
		preload(file_name, online = False, pins = {"in": [], "out": [buzzer_pin, red_led, green_led, triger_pin]}) 
		
		log_and_run(run)
				
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)
