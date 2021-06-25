import os 
import sys
import time
import datetime
import traceback
import unittest
import string
import readchar
import datetime
from random import *
import os.path
from os import path

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
requests.packages.urllib3.disable_warnings()

import RPi.GPIO as GPIO

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)



buzzer_pin = 4 #buzzer_pin = 7  //7. bacak GPIO4
red_led = 23#red_led = 16
green_led = 24#green_led = 18
triger_pin = 17#triger_pin = 11

local_debug = False


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
		print(msg)
		
		while True:
			if h.loop == False: break
			
			try:	
				card_id = get_card_id_from_rfid()
				if card_id != None:
					print("Card ID: " + card_id)
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
		global local_debug
		h.debug = True
		
		random_str = self.get_random_str()		
		log(INFO, "Random str for log test: " + random_str)		
		lastLine = self.get_last_line_from_current_log_file()
		
		try:
			lastLine.index(random_str)
			self.assertEqual(True, True, "Temp")
		except Exception as e:
			self.assertEqual(False, True, "Log file must has random_str:" + random_str)
			
		h.debug = local_debug
			
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
		global local_debug
		h.debug = True
		
		self.temp = False
		
		h.log_and_run(self.control)
		
		lastLine = self.get_last_line_from_current_log_file()
		
		self.assertEqual(self.temp, True, "Should be true")
		
		try:
			lastLine.index('INFO - "control" OK')
			self.assertEqual(True, True, "Temp")
		except Exception as e:
			self.assertEqual(False, True, "Log file must has info for log_and_run operations (lastLine: " + lastLine + ")")
			
		h.debug = local_debug
			
	def test_log_and_run_async(self):		
		global local_debug
		h.debug = True
		
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
			
		h.debug = local_debug
			
	def test_take_photo(self):
		name = take_photo()
		self.assertIsNotNone(name, "name should not be None")
		
		c = os.path.isfile(h.base_photo_path+name)
		self.assertEqual(c, True, "File should be exist in dir: " + h.base_photo_path+name)
		
		os.remove(h.base_photo_path+name)
		
		
		name = self.get_random_str() + ".jpg"
		tempName = take_photo(name)

		self.assertIsNotNone(tempName, "name should not be None")
		self.assertEqual(tempName, name, "name should be equal tempName")
		
		
		c = os.path.isfile(h.base_photo_path+name)
		self.assertEqual(c, True, "File should be exist in dir: " + h.base_photo_path+name)
		
		os.remove(h.base_photo_path+name)
		
	def test_get_card_id_from_rfid(self):
				
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
		self.assertEqual(2, h.rfid_same_count, "Should be 2")
		
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
			
	#TODO: limit_bandwith && unlimit_bandwith
	
	def test_download_file(self):
		path = "img/logo.png"
		name= "wgetDeneme.png"
		url = "https://kamu.kutahya.gov.tr/uploads/2021/01/01/mesaiTakipCihazi/"
		
		temp = download_file(url+path, h.base_photo_path+name, sllDisable=True)
		size = os.stat(h.base_photo_path+name).st_size
		self.assertGreater(size,0,"File size greather then 0")

		file_exist = os.path.exists(h.base_photo_path+name)
		self.assertEqual(file_exist,True,"Should be True")
		os.remove(h.base_photo_path+name)

	def test_http_get(self):
		temp = http_get(h.api_base_url)
		self.assertEqual(temp, '{"status":"success","code":200,"data":{"message":"service.ok"}}', "Should be txt")

		temp = http_get(h.api_base_url, j = True)
		self.assertEqual(temp["status"], 'success', "Should be Json")

		temp = http_get(h.api_base_url, return_raw = True)
		self.assertEqual(temp.json()["status"], 'success', "Should be raw")

	def test_http_post(self):
		temp = http_post(h.api_base_url)
		self.assertEqual(temp, '{"status":"success","code":200,"data":{"message":"service.ok"}}', "Should be txt")

		temp = http_post(h.api_base_url, j = True)
		self.assertEqual(temp["status"], 'success', "Should be Json")
		
		temp = http_post(h.api_base_url, return_raw = True)
		self.assertEqual(temp.json()["status"], 'success', "Should be raw")
		
	def test_encode_url(self):
		url = h.api_base_url
		param = url.replace(":","%3A")
		temp = encode_url(url)
		self.assertEqual(temp, param,"Should be encode_url")

	def test_get_url_for_rfid_readed(self):
		fill_auth()		
		token = h.auth["token"]
		card_id = self.read_rfid(msg = "Kart okutunuz...")
		encode_card_id =card_id.replace(" ", "%20")

		#EMPTY DAY, TODAY , PREV DAY , NEXT DAY
		empty_day = get_url_for_rfid_readed(card_id)
		self.assertEqual(empty_day,h.api_base_url+"device/"+token+"/rfidReaded?card_id="+encode_card_id + "&time=now","Should be error url")
		
		to_day = datetime.datetime.now()
		current_time = to_day.strftime("%Y-%m-%d %H:%M:%S")		
		today_day = get_url_for_rfid_readed(card_id,current_time)
		self.assertEqual(today_day,h.api_base_url+"device/"+token+"/rfidReaded?card_id="+encode_card_id + "&time="+encode_url(current_time),"Should be error url")
		
		prev_date = datetime.datetime.now() - datetime.timedelta(1)
		prev_time = prev_date.strftime("%Y-%m-%d %H:%M:%S")
		prev_day = get_url_for_rfid_readed(card_id, prev_time)
		self.assertEqual(prev_day,h.api_base_url+"device/"+token+"/rfidReaded?card_id="+encode_card_id + "&time="+encode_url(prev_time),"Should be error url")
		
		#TODO 300 gun oncesi icin de bir tet yaz error donecek

		next_date = datetime.datetime.now() + datetime.timedelta(1)
		next_time = next_date.strftime("%Y-%m-%d %H:%M:%S")
		next_day = get_url_for_rfid_readed(card_id, next_time)
		self.assertEqual(next_day,h.api_base_url+"device/"+token+"/rfidReaded?card_id="+encode_card_id + "&time="+encode_url(next_time),"Should be error url")
		
		empty_post = http_post(empty_day)
		today_post = http_post(today_day)
		next_post = http_post(next_day)
		prev_post = http_post(prev_day)
		self.assertEqual(json.loads(empty_post)['status'],"success","Must be success")
		self.assertEqual(json.loads(today_post)['status'],"success","Must be success")
		self.assertEqual(json.loads(next_post)['status'],"success","Must be success")
		self.assertEqual(json.loads(prev_post)['status'],"success","Must be success")

	def test_get_url_for_send_photo(self):
		fill_auth()
		token = h.auth["token"]
		url = "https://kamu.kutahya.gov.tr/api/v1/"
		temp = get_url_for_send_photo()
		param = url+"device/"+token+"/sendPhoto"
		self.assertEqual(temp,param, "Should be https://kamu.kutahya.gov.tr/api/v1/device/token/sendPhoto")

	def test_get_url_for_users_list(self):
		fill_auth()
		token = h.auth["token"]
		url = "https://kamu.kutahya.gov.tr/api/v1/"
		temp = get_url_for_users_list()
		param = url+"device/"+token+"/getUsersList"
		self.assertEqual(temp,param, "Should be https://kamu.kutahya.gov.tr/api/v1/device/token/sendPhoto")

	def test_get_mac_adresses(self):
		cmd = "ip addr | grep ether | awk -F ' ' '{print $2}'"
		output = command(cmd) 
		param = output.split("\n")
		temp = get_mac_adresses()
		self.assertEqual(temp, param, "Must be the same ")
		
	def test_get_ip_adresses(self):
		cmd = "ip addr | grep 'inet ' | awk -F ' ' '{print $2}'"
		output = command(cmd) 
		param = output.split("\n")
		temp = get_ip_adresses()
		self.assertEqual(temp,param, "Must be the same ")

	def test_get_cpu_serial(self):
		cpuserial = ""
		try:
			f = open("/proc/cpuinfo","r")
			for line in f:
				if line[0:6]=="Serial":
					cpuserial = line[10:26]
			f.close()
		except:
			cpuserial = ""
	
		param = get_cpu_serial()
		self.assertEqual(cpuserial,param, "Must be the same ")

	def test_connection_control(self):
		h.connected = False
		h.request_using = True
		connection_control()
		self.assertEqual(h.connected, False, "Must be the true ")

		h.request_using = False
		connection_control()
		self.assertEqual(h.connected, True, "Must be the true ")
	
	def test_to_json_str(self):
		temp = ["data","success"]
		param = to_json_str(temp)
		self.assertEqual(param,'["data", "success"]', "Data must be the same ")

	def test_from_json_str(self):
		s = '{"data": "success"}'
		obj = from_json_str(s)
		self.assertEqual(obj, {"data": "success"}, "Must be the same ")
	
	def test_write_to_file(self):
		test_file_url = "/var/www/html/file/testwritefile.json"
		temp = 'string'
		write_to_file(test_file_url,temp)
		f = open(test_file_url, "r")
		readed = f.read()
		f.close()
		self.assertEqual(readed, 'string', "Must be the same ")
		os.remove(test_file_url)
		
		obj = {"data":"success"};
		write_to_file(test_file_url, obj, j=True)
		f = open(test_file_url, "r")
		readed = f.read()
		f.close()
		self.assertEqual(readed, h.to_json_str(obj), "Must be the same ")
		os.remove(test_file_url)

	def test_get_real_ip(self):
		temp = h.get_real_ip().split(".")
		self.assertEqual(len(temp),4, "Must be 4")
	
	def test_read_from_file(self):
		test_file_url = "/var/www/html/file/testreadfile.json"
		temp = '{"data":"success"}'
		write_to_file(test_file_url,temp)

		param = read_from_file(test_file_url)
		self.assertEqual(param, temp, "Must be the same ")

		obj = read_from_file(test_file_url, j=True)
		self.assertEqual(obj["data"], "success", "Must be the same ")

		os.remove(test_file_url)
	
	def test_fill_auth(self):
		temp = os.path.isfile(h.auth_file_path)
		if temp:
			os.remove(h.auth_file_path)

		fill_auth(True)
		temp = os.path.isfile(h.auth_file_path)
		self.assertEqual(temp, True, "Must be True")

		auth = read_from_file(h.auth_file_path, j=True)
		
		self.assertEqual("token" in auth.keys(), True, "Auth must has token attribute")

	def test_fill_users(self):
		temp = os.path.isfile(h.users_list_path)
		if temp:
			os.remove(h.users_list_path)

		fill_users(True)
		temp = os.path.isfile(h.users_list_path)
		self.assertEqual(temp, True, "Must be True")

		users = read_from_file(h.users_list_path, j=True)
		
		try:
			temp = len(list(users.keys())[0].split(" ")) == 4
			self.assertEqual(temp, True, "Users must has rfid attribute")
		except Exception as e:
			log_e(e, "Users validation exception")
			self.assertEqual(False, True, "Users must has rfid attribute...")



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