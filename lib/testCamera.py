import os 
import sys
import json
import time
import traceback

import RPi.GPIO as GPIO

from helper import *
import helper as h

file_name = os.path.basename(__file__)
	

try:
		
	#Ana Fonksiyon
	if __name__ == "__main__":	
	
		preload(file_name, online = False, cam = True) 
		
		log_and_run(take_photo, "omer.jpg")
				
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)
