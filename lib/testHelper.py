import os 
import sys
import time
import datetime
import traceback
import unittest
import string
from random import *
import readchar

import RPi.GPIO as GPIO

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)



buzzer_pin = 4 #buzzer_pin = 7  //7. bacak GPIO4
red_led = 23#red_led = 16
green_led = 24#green_led = 18
triger_pin = 17#triger_pin = 11

local_debug = True



class TestSum(unittest.TestCase):

	####   Variables	####
	
	temp = False
	
	
	
	####	Helper Functions	####
	
	def get_random_str(self):
		allchar = string.ascii_letters + string.digits
		return "".join(choice(allchar) for x in range(randint(8, 12)))
		
	def get_last_line_from_current_log_file(self):
		global file_name
		
		logFile = open(h.log_base_path+file_name+".log", "r")
		logs = logFile.readlines()
		logFile.close()
		return logs[-1]
		
	def control(self):
		self.temp = True
		
	def read_rfid(self, msg = "Kart okutunuz...."):		
		log(INFO, msg)
		
		while True:
			if h.loop == False: break
			
			try:	
				card_id = get_card_id_from_rfid()
				if card_id != None:
					log(INFO, "Card ID: " + card_id)
					return card_id
					
			except Exception as e:
				log_e(e, "Rfid read error")



	####	Test Functions	####
	
	def test_start(self):
		self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
	
	#TODO: test_root_ex

	def test_run_dynamic_function(self):
		h.temp = False
		h.run_dynamic_function("run_dynamic_function_test")
		self.assertEqual(h.temp, True, "Should be True")
		
	def test_log(self):
		random_str = self.get_random_str()		
		log(INFO, "Random str for log test: " + random_str)		
		lastLine = self.get_last_line_from_current_log_file()
		
		try:
			lastLine.index(random_str)
			self.assertEqual(True, True, "Temp")
		except Exception as e:
			self.assertEqual(False, True, "Log file must has random_str:" + random_str)
			
	def test_log_e(self):
		try:
			temp = 6 / 0
		except Exception as e:
			random_str = self.get_random_str()
			log_e(e, "Random str for log_e test: " + random_str)
			lastLine = self.get_last_line_from_current_log_file()
			
			try:
				lastLine.index(random_str)
				self.assertEqual(True, True, "Temp")
			except Exception as e:
				self.assertEqual(False, True, "Log file must has random_str (for log_e):" + random_str)
				
	def test_log_and_run(self):
		self.temp = False
		
		h.log_and_run(self.control)
		
		lastLine = self.get_last_line_from_current_log_file()
		
		self.assertEqual(self.temp, True, "Should be true")
		
		try:
			lastLine.index('INFO - "control" OK')
			self.assertEqual(True, True, "Temp")
		except Exception as e:
			self.assertEqual(False, True, "Log file must has info for log_and_run operations (lastLine: " + lastLine + ")")
			
	def test_log_and_run_async(self):
		self.temp = False
		
		h.log_and_run_async(self.control)
		
		time.sleep(2)
		lastLine = self.get_last_line_from_current_log_file()
		
		self.assertEqual(self.temp, True, "Should be true")
		
		try:
			lastLine.index('INFO - "control" trigger OK (async)')
			self.assertEqual(True, True, "Temp")
		except Exception as e:
			self.assertEqual(False, True, "Log file must has info for log_and_run operations (lastLine: " + lastLine + ")")
			
	def test_take_photo(self):
		name = take_photo()
		self.assertIsNotNone(name, "name should not be None")
		
		c = os.path.isfile(h.base_photo_path+name)
		self.assertEqual(c, True, "File should be exist in dir: " + h.base_photo_path+name)
		
		os.remove(h.base_photo_path+name)
		
		
		name = self.get_random_str() + ".jpg"
		name = take_photo(name)
		self.assertIsNotNone(name, "name should not be None")
		
		c = os.path.isfile(h.base_photo_path+name)
		self.assertEqual(c, True, "File should be exist in dir: " + h.base_photo_path+name)
		
		os.remove(h.base_photo_path+name)
		
	"""def test_get_card_id_from_rfid(self):
				
		h.last_rfid_card_id = ""
		h.rfid_same_count = 5
		
		card_id = self.read_rfid(msg = "Kart okutunuz...")
		self.assertIsNotNone(card_id, "card_id should not be None")
							
		temp = card_id.split(" ")
		self.assertEqual(str(type(temp)), "<class 'list'>", "Should be list")
		self.assertEqual(len(temp), 4, "Len is should be 4")
		
		self.assertEqual(card_id, h.last_rfid_card_id, "Should be equal")
		
		self.assertEqual(1, h.rfid_same_count, "Should be 1")
		
		self.read_rfid(msg = "Ayni karti okutunuz...")
		self.assertEqual(2, h.rfid_same_count, "Should be 2")"""
		
	def test_pin(self):
	
		global green_led
		
		pin_on(green_led, 1)
		
		state = GPIO.input(green_led)
		self.assertEqual(state, True, "File should be True")
		
		time.sleep(1.1)
		
		state = GPIO.input(green_led)
		self.assertEqual(state, False, "File should be False")
		
	def test_display(self):
	
		displays = ['oled']
		for i in range(len(displays)):
			h.default_display = displays[i]
			
			write_logo_on_display()
			print("Is logo show on "+h.default_display+"? [y/n]")
			r = str(readchar.readkey())
			self.assertEqual(r, "y", "Key should be y")
			
			sizes = write_text_on_center_of_display("center text", x = 0, y = 0, font_size = 12, font_path = "", direction = "xy")
			print("Is text show center on "+h.default_display+"? [y/n]")
			r = str(readchar.readkey())
			self.assertEqual(r, "y", "Key should be y")
			
			write_text_on_display("normal text", x = 0, y = 0, font_size = 12, font_path = "")
			print("Is text show top-left on "+h.default_display+"? [y/n]")
			r = str(readchar.readkey())
			self.assertEqual(r, "y", "Key should be y")
			
			clean_area_on_display(sizes, write_now = True)
			print("Was center text clean on "+h.default_display+"? [y/n]")
			r = str(readchar.readkey())
			self.assertEqual(r, "y", "Key should be y")
			
			clear_display()
			print("Was "+h.default_display+" clean? [y/n]")
			r = str(readchar.readkey())
			self.assertEqual(r, "y", "Key should be y")
	
	
	
	
	
	
	#TODO: exit
	
	
	
	
	
	
	
	#TODO: test_end_load

	#TODO: reboot_os

try:	
	def run():
		unittest.main()
		
		
		
	#Ana Fonksiyon
	if __name__ == "__main__":	
				
		time.sleep(1)
		
		h.restart = False
		h.loop = True
		h.debug = local_debug;
		
		pin_config = {"in": [], "out": [buzzer_pin, red_led, green_led, triger_pin]}
		
		preload(file_name, online = True, disp = "oled", cam = True, rf = True, pins = pin_config) 
				
		log_and_run(run)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)