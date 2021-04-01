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
	
		preload(file_name, online = False, disp = 'oled') 
		
		"""str = "Kutahya Il Ozel Idrei - Bilg Islem Mudurlugu"
		sizes = write_text_on_display(str, x = 20, y = 22, font_size = 36)
		print(sizes)
		clean_area_on_display(sizes, write_now = True)"""
		
		"""log_and_run(write_logo_on_display)
		
		time.sleep(1)
		
		
		sizes = write_text_on_display("omersaas", x = 0, y = 0, font_size = 12, font_path = "", disp = "oled")
		write_text_on_display("omersaas", x = 0, y = 0, font_size = 26, font_path = "", disp = "oled")
		
		clean_area_on_display(sizes, write_now = True, disp = 'oled')
		
		
		clear_display()
		write_text_on_display("omersaas", x = 0, y = 0, font_size = 26, font_path = "", disp = "oled")
		
		
		
		
		clear_display()
		
		write_text_on_display("23 Mar 15:12", font_size = 16)
		
		str = "Kutahya Il Ozel Idrei - Bilg Islem Mudurlugu    "
		
		h.loop = True
		
		h.debug = False
		
		current_x = 10
		sizes = [0, 0, 0, 0]
		while True:
			clean_area_on_display(sizes)
			sizes = write_text_on_display(str, x = current_x, y = 22, font_size = 36)
			#print(sizes)
			current_x = current_x - 7
			#time.sleep(0.02)
			if h.loop == False:
				break;"""
				
				
		clear_display()
		
		write_text_on_center_of_display("Mehmet Sefa", y = 5, font_size = 20)
		write_text_on_center_of_display("ORTAAKARSU", y=32, font_size = 20)
				
		
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)
