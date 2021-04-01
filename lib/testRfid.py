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
		h.loop = True
		
		while True:
			card_id = get_card_id_from_rfid()
			print(card_id)
			time.sleep(0.2)
			if h.loop == False:
				break;
		
		
	#Ana Fonksiyon
	if __name__ == "__main__":	
	
		preload(file_name, online = False, rf = True) 
		
		log_and_run(run)
				
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)
