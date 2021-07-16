####	IMPORTS	####

import sys
import os
import logging

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import json
import signal
import threading
import traceback
import time
import string
from random import *

import urllib.parse

import MFRC522

import RPi.GPIO as GPIO

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import picamera

from variables import *



####	VARIABLES	####

logger = None

log_base_path = "/var/www/html/log/"
lib_base_path = "/var/www/html/lib/"
app_base_path = "/var/www/html/"
dateTimeSync_py_file_path = "/var/www/html/dateTimeSync.py"
auth_file_path = "/var/www/html/file/auth.json"
users_list_path = "/var/www/html/file/users.json"
auth_py_file_path = "/var/www/html/auth.py"
update_users_list_py_file_path = "/var/www/html/updateUsersList.py"
after_update_subs_py_file_path = "/var/www/html/afterUpdateSubscriber.py"
logo_path = "/var/www/html/img/logo.png"
base_font_path = "/var/www/html/font/lato.ttf"
base_photo_path = "/var/www/html/foto/"

months = ["Oca", "Sub", "Mar", "Nis", "May", "Haz", "Tem", "Agu", "Eyl", "Eki", "Kas", "Ara"]

restart = False
started = False
debug = False
loop = False
last_response = None

INFO = 1
WARNING = 2
ERROR = 3

connected = False
connection_control_timer_period = 50.0
connection_controling = False

auth = None

default_display = "oled"
display_clear_seq = 0

oled = None
oled_data = None

camera = None

rfid = None
last_rfid_card_id = ""
rfid_same_count = 1

request_using = False
requests_timeout = 5 

users = {}

temp = False

fileName = ""

#### FUNCTIONS	####

def root_ex(file_name, e):
	global restart, started, log_base_path
	
	def log_temp(l, s):
		m = "Level: " + str(l) + " - " + str(s)
		print(m)
		
		with open(log_base_path+file_name+".log", "a") as f:
			f.write(m+"\n")	
	
	arr = traceback.format_exc().strip("\n").split("\n");
	ln = len(arr)
	
	m = " [ E: "+ arr[ln-1].strip()
	m = m + ", L: " + arr[ln-3].strip()
	m = m + ", C: " + arr[ln-2].strip()+" ]"
	
	log_temp(ERROR, "General error! " + m)
	
	if restart:
		if started:
			log_temp(WARNING, "Rebooting...")
			os.system("python "+app_base_path+file_name) 
		else:
			log_temp(WARNING, "Error in preload! Will not reboot.")
			GPIO.cleanup()
	else:
		log_temp(WARNING, "Will not reboot")
		GPIO.cleanup()
		
		
def preload(log_file_name, online = True, disp = "no", cam = False, pins = None, rf = False):	
	global started, fileName
	
	fileName = log_file_name
	
	log_init(log_file_name)	
	log(INFO, "Starting...")
	
	signal.signal(signal.SIGINT, exit)
	
	if disp != "no":
		log_and_run(display_init, disp)
		
	if cam:
		log_and_run(camera_init)
		
	if pins != None:
		log_and_run(pins_init, pins)
		
	if rf:
		log_and_run(rfid_init)
	
	log(INFO, "Start OK")
	started = True
	
	log_and_run(unlimit_bandwith)
	
	if online:
		log_and_run(connection_control)
	
def endload():
	global loop
	loop = False
	
	GPIO.setwarnings(False)
	GPIO.cleanup()
	
	log(INFO, "Tamamlandi!")
		
def log_init(log_file_name):	
	global log_base_path, logger
	
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	handler = logging.FileHandler(log_base_path+log_file_name+".log")
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)

	logger.addHandler(handler)
	
	log(INFO, "Log init OK")
	
def run_dynamic_function(fn_name, params = None):
	fnc = globals()[fn_name]
	return log_and_run(fnc, params)
	
def run_dynamic_function_test():
	global temp
	temp = True
		
def display_init(disp = default_display):
	return run_dynamic_function(disp+"_display_init")
		
def oled_display_init():		
	global oled, i2c, oled_data
	
	i2c = busio.I2C(SCL, SDA)
	oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
	
	log_and_run(clear_oled)
	
def camera_init():
	global camera, base_photo_path
	
	camera = picamera.PiCamera()
	log_and_run(create_dir_if_not_exist, base_photo_path)	
	
def pins_init(pins):
	GPIO.setmode(GPIO.BCM)
	
	for i in range(len(pins["in"])):
		GPIO.setup(pins["in"][i], GPIO.IN)
		
	for i in range(len(pins["out"])):
		GPIO.setup(pins["out"][i], GPIO.OUT)
		
def rfid_init():
	global rfid
	rfid = MFRC522.MFRC522()
	
def log(l, s):
	global debug
	
	if debug:
		_log(l, s)
	elif l > 1:
		_log(l, s)
			
def _log(l, s):
	global logger
		
	if l == 3:
		logger.error("%s", str(s))
	elif  l == 2:
		logger.warning("%s", str(s))
	else:
		logger.info("%s", str(s))
		
	print("LOG -> level:" + str(l) + " - " + str(s))
	
def log_e(e, m):
	arr = traceback.format_exc().strip("\n").split("\n");
	ln = len(arr)
	
	m = m + " [ E: "+ arr[ln-1].strip()
	m = m + ", L: " + arr[ln-3].strip()
	m = m + ", C: " + arr[ln-2].strip()+" ]"
	
	log(ERROR, m)
	
def log_and_run(fnc, params = None):
	log(INFO, '"' + fnc.__name__  + '" running...')
	
	try:
		if type(params) == type(None):
			r = fnc()
		else:
			r = fnc(params)
			
		log(INFO, '"' + fnc.__name__  + '" OK')
		
		return r
	except Exception as e:
		log_e(e, '"' + fnc.__name__  + '" end with error')

def log_and_run_async(fnc, params = [], time_out = 0):
	log(INFO, '"' + fnc.__name__  + '" running (async)...')
	
	try:	
		i = threading.Thread(target=fnc, args = params)
		i.start()
		
		if float(time_out) > 0.0:
			log(INFO, "Wait for async function "' + fnc.__name__  + '" :" + str(time_out))
			i.join(float(time_out))
				
		log(INFO, '"' + fnc.__name__  + '" trigger OK (async)')
		
	except Exception as e:
		log_e(e, '"' + fnc.__name__  + '" end with error (async)')
		
def take_photo(name = ""):	
	global camera, base_photo_path 
	
	if camera == None:
		log(INFO, "Take photo error. Camera is None")
		return;	
	
	if name == "":
		min_char = 8
		max_char = 12
		allchar = string.ascii_letters + string.digits
		name = "".join(choice(allchar) for x in range(randint(min_char, max_char))) + ".jpg"
	
	camera.capture(base_photo_path + name)
			
	return name
	
def get_card_id_from_rfid():
	global rfid, last_rfid_card_id, rfid_same_count
	
	if rfid == None:
		log(INFO, "Rfid read error. Rfid is None")
		return;	
	
	try:	
		(status, TagType) = rfid.MFRC522_Request(rfid.PICC_REQIDL)
		if status == rfid.MI_OK:
			(status, uid) = rfid.MFRC522_Anticoll()
			if status == rfid.MI_OK:
				temp = str(uid[0]) + " " + str(uid[1]) + " " + str(uid[2]) + " " + str(uid[3])
				
				if last_rfid_card_id == temp:
					rfid_same_count = rfid_same_count + 1
				else:
					rfid_same_count = 1
					
				last_rfid_card_id = temp
				return last_rfid_card_id
				
	except Exception as e:
		log_e(e, "Rfid read error")
			
		
def pin_on(pin, time_out = -1.0):
	try:
		GPIO.output(pin, 1)
		
		if time_out != -1.0:
			temp = threading.Timer(time_out, pin_off, [pin])
			temp.daemon = True
			temp.start()
	except Exception as e:
		log_e(e, "Led on end with error")
		
def pin_off(pin):
	try:
		GPIO.output(pin, 0)	
	except Exception as e:
		log_e(e, "Led off end with error")

def exit(signal, frame):
	global loop
	loop = False
	log(INFO, "Exit...")
	sys.exit()
	
def reboot_os():
	global app_base_path
	
	log(WARNING, "Rebooting...")	
	
	loop = False
	
	time.sleep(2)
	os.system("sudo reboot")
	time.sleep(2)
	sys.exit()	
	
def write_logo_on_display(disp = default_display):
	run_dynamic_function("write_logo_on_"+disp)
	
def write_logo_on_oled():
	global logo_path, oled
	
	if oled == None:
		log(INFO, "Write logo on oled error. Oled is None")
		return;	
	
	image = (
		Image.open(logo_path)
		.resize((oled.width, oled.height), Image.BICUBIC)
		.convert("1")
	)

	oled.image(image)
	oled.show()
	
def write_text_on_center_of_display(text, x = 0, y = 0, font_size = 12, font_path = "", disp = default_display, direction = "x"):
	params = {
		"text": text,
		"x": x,
		"y": y,
		"font_size": font_size,
		"font_path": font_path,
		"direction": direction
	}
	
	return run_dynamic_function("write_text_on_center_of_"+disp, params)
	
def write_text_on_center_of_oled(params):
	global base_font_path, oled, oled_data
	
	if oled == None:
		log(INFO, "Write text on center of oled error. Oled is None")
		return;	
	
	if params["font_path"] == "":
		params["font_path"] = base_font_path
		
	font = ImageFont.truetype(params["font_path"], params["font_size"])
	wd, hg = oled_data["draw"].textsize(params["text"], font=font)
	
	if params["direction"] == "x":
		params["x"] = (oled.width - wd) / 2
	elif params["direction"] == "y":	
		params["y"] = (oled.height - hg) / 2
	else:
		params["x"] = (oled.width - wd) / 2
		params["y"] = (oled.height - hg) / 2
		
	return write_text_on_oled(params)
	
def write_text_on_display(text, x = 0, y = 0, font_size = 12, font_path = "", disp = default_display):
	params = {
		"text": text,
		"x": x,
		"y": y,
		"font_size": font_size,
		"font_path": font_path
	}
	
	return run_dynamic_function("write_text_on_"+disp, params)
	
def write_text_on_oled(params):
	global base_font_path, oled, oled_data
	
	if oled == None:
		log(INFO, "Write text on oled error. Oled is None")
		return;	
	
	if params["font_path"] == "":
		params["font_path"] = base_font_path
	
	font = ImageFont.truetype(params["font_path"], params["font_size"])	
	oled_data["draw"].text((params["x"], params["y"]), params["text"], font=font, fill=255)
		
	oled.image(oled_data["image"])
	oled.show()
	
	w, h = oled_data["draw"].textsize(params["text"], font=font)
	
	w = w + params["x"]
	h = h + params["y"]
	
	if w > oled.width:
		w = oled.width
		
	if h > oled.height:
		h = oled.height
		
	return [params["x"], params["y"], w, h]
	
def clean_area_on_display(sizes, write_now = False, disp = default_display):

	params = {
		"sizes": sizes,
		"write_now": write_now
	}
	
	run_dynamic_function("clean_area_on_"+disp, params)
	
def clean_area_on_oled(params):
	global oled, oled_data
	
	if oled == None:
		log(INFO, "Clean area on oled error. Oled is None")
		return;	
	
	oled_data["draw"].rectangle(params["sizes"], outline=0, fill=0)
	
	if params["write_now"]:
		oled.image(oled_data["image"])
		oled.show()
		
def clear_display(disp = default_display):
	global display_clear_seq
	display_clear_seq = display_clear_seq + 1
	
	return run_dynamic_function("clear_"+disp)
	
def clear_oled():
	global oled, oled_data
	
	if oled == None:
		log(INFO, "Clear oled error. Oled is None")
		return;	
	
	oled.fill(0)
	oled.show()
	
	image = Image.new("1", (oled.width, oled.height))
	draw = ImageDraw.Draw(image)
	
	oled_data = {
		"image": image,
		"draw": draw
	}
	
def limit_bandwith(eth = "eth0", u = 512, d = 1024):
	command("wondershaper "+eth+" "+str(d)+" "+str(u))
	
def unlimit_bandwith(eth = "eth0"):
	command("wondershaper clear "+eth)
	
def download_file(url, path, sllDisable = False):
	try:
		log(INFO, "Download file ("+url+", "+path+")")
		
		cmd = "wget -O "+path+" "+url
		if sllDisable:
			cmd = cmd +" --no-check-certificate"
			
		temp = command(cmd)
		return True
		
	except Exception as e:
		return False
	
def http_get(url, return_raw = False, j = False, force = False, to = requests_timeout):	
	global last_response, connected, lib_base_path, request_using, sll_verify
	
	try:
		log(INFO, "Http GET ("+url+")")
		
		if connected == False and force == False:
			log(INFO, "Http GET by pass")
			return
			
		last_response = None		
		request_using = True
		
		rt = requests.get(url, verify=sll_verify, timeout=to)
		last_response = rt.text
		
		if return_raw:			
			log(INFO, "Http GET OK (RAW)")
			request_using = False
			return rt
		elif j:
			r = rt.json()
			log(INFO, "Http GET OK (JSON)") 
			request_using = False
			return r
		
		log(INFO, "Http GET OK (TXT)")
		request_using = False
		
		return last_response		
		
	except Exception as e:
		
		request_using = False
		
		try:
			text = rt.text
		except:
			text = ""
			
		log_e(e, "Http GET ERROR (url: " + url + ", text: "+text+")")
		last_response = None

def http_post(url, data = None, files = None, return_raw = False, j = False, force = False, to = requests_timeout):		
	global last_response, lib_base_path, request_using, connected, sll_verify
		
	try:
		log(INFO, "Http POST ("+url+")")

		if connected == False and force == False:
			log(INFO, "Http POST by pass")
			return		
		
		last_response = None		
		request_using = True
		
		rt = requests.post(url, data=data, files=files, verify=sll_verify, timeout=to)
		last_response = rt.text
		
		if return_raw:
			log(INFO, "Http POST OK (RAW)")
			request_using = False
			return rt
		elif j:
			r = rt.json()
			log(INFO, "Http POST OK (JSON)")
			request_using = False
			return r
		
		log(INFO, "Http POST OK (TXT)")
		request_using = False
		return last_response		
		
	except Exception as e:
		request_using = False
		
		try:
			text = rt.text
		except:
			text = ""
			
		log_e(e, "Http POST ERROR (url: " + url + ", data: "+to_json_str(data)+ ", files: "+to_json_str(files)+", text:"+text+")")
		last_response = None
		
def encode_url(url):
	return urllib.parse.quote(url)
	
def get_url_for_rfid_readed(card_id, date_time = "now"):
	global api_base_url, auth
	
	if auth == None:
		return ""	

	return api_base_url + "device/" + auth["token"] + "/rfidReaded?card_id=" + encode_url(card_id) + "&time="+encode_url(date_time)
	
def get_url_for_deg_device_key():
	global api_base_url, get_device_key_url_path
	return api_base_url + get_device_key_url_path
	
def get_url_for_last_activity():
	global api_base_url, auth
	
	if auth == None:
		return api_base_url	

	return api_base_url + "device/" + auth["token"] + "/lastActivity"
	
def get_url_for_send_photo():
	global api_base_url, auth
	
	if auth == None:
		return ""	
	
	return api_base_url + "device/" + auth["token"] + "/sendPhoto"
	
def get_url_for_users_list():
	global api_base_url, auth
	
	if auth == None:
		return ""	
	
	return api_base_url + "device/" + auth["token"] + "/getUsersList"

def get_mac_adresses():
	log(INFO, "Get mac adresses")
	
	cmd = "ip addr | grep ether | awk -F ' ' '{print $2}'"
	output = command(cmd) 
	r = output.split("\n")
	
	log(INFO, "Mac adresses OK : " +str(r))
	return r
		
def get_ip_adresses():
	log(INFO, "Get IP adresses")
	
	cmd = "ip addr | grep 'inet ' | awk -F ' ' '{print $2}'"
	output = command(cmd) 
	r = output.split("\n")
		
	log(INFO, "IP adresses OK : " +str(r))
	return r
	
def get_cpu_serial():	
	log(INFO, "Get CPU serial")
	
	cpuserial = ""
	try:
		f = open("/proc/cpuinfo","r")
		for line in f:
			if line[0:6]=="Serial":
				cpuserial = line[10:26]
		f.close()
	except:
		cpuserial = ""
		
	log(INFO, "CPU serial OK : " + cpuserial)
	return cpuserial
	
def restart_ip():
	log(INFO, "Trying restart IP")
	command("systemctl restart dhcpcd")  	
	log(INFO, "Restart IP ok")
	
def connection_control():
	log(INFO, "Connection control")
	global connected, loop, connection_control_timer_period, request_using, connection_controling, started, fileName
	
	temp = threading.Timer(connection_control_timer_period, connection_control)
	temp.daemon = True
	temp.start()
		
	if request_using:
		log(INFO, "Connection control by pass")
		return
		
	if connection_controling:		
		log(INFO, "Connection control by pass (connection_controling)")
		return		
		
	connection_controling = True
	
	try:
		
		url = log_and_run(get_url_for_last_activity)
		data = http_get(url, j=True, force=True)
		
		if data == None:			
			log(INFO, "Connection control error.")
			connected = False
			connection_controling = False
			return
		
		if data["status"] != "success":
			log(INFO, "Connection control error")
			connected = False
			connection_controling = False
			return
		
		if connected == True:
			log(INFO, "Connection control continue as True")
			connection_controling = False
			return
			
		if started != True:
			log(INFO, "Connection control OK (started: False)")
			connection_controling = False
			connected = True	
			return
		
		if fileName != "main.py":	
			log(INFO, "Connection control OK")
			connected = True	
			connection_controling = False		
			return
		
		log(INFO, "Connection changed False to True. Try fill auth and users")
		
		log_and_run(sync_date_time)
		
		temp = log_and_run(fill_auth, True)
		if temp == True:
			temp = log_and_run(fill_users, True)
			
		if temp == True:				
			connected = True			
			log(INFO, "Connection control OK")
		else:
			log(INFO, "Connection control OK but Auth or Users fail")
				
	except Exception as e:
		connected = False
		log_e(e, "Connection control error (ex).")
	
	connection_controling = False
	
def to_json_str(o):
	try:
		return json.dumps(o)
	except Exception as e:
		log_e(e, "Json parse error in to_json_str");
		return ""
		
def from_json_str(str):
	try:
		return json.load(str) 
	except Exception as e:
		try:
			return json.loads(str)
		except Exception as e:
			log_e(e, "Json encode error in from_json_str");
			return None
	
def create_dir_if_not_exist(dir):
	if os.path.isdir(dir) == False:
		os.makedirs(dir)
	
def write_to_file(path, data, j = False):
	try:
		log(INFO, "Trying write to file...")
		
		temp = os.path.dirname(path)
		log_and_run(create_dir_if_not_exist, temp)		
		
		if j:
			data = to_json_str(data)
			
		f = open(path, "w")
		f.write(data)
		f.close()
		
		log(INFO, "Write to file OK")
	
	except Exception as e:
		log_e(e, "Write to file error")
	
def get_real_ip():
	log(INFO, "Trying get real IP")
	
	u = "https://api64.ipify.org?format=json"
	data = http_get(u, force=True, j=True)
	
	if data == None:
		log(INFO, "Get real IP error")
		return None
	else:
		log(INFO, "Get real IP success ("+to_json_str(data)+")")
		return data["ip"]
		
def read_from_file(file_path, j=False):
	try:
		log(INFO, "Trying read from file...")
		
		f = open(file_path, "r")
		r = f.readlines()
		f.close()
		
		rt = "".join(r)
		
		log(INFO, "Read from file OK ( "+rt+" )")
		
		if j:
			return log_and_run(from_json_str, rt)
			
		return rt
		
	except Exception as e:
		log_e(e, "Read from file error ("+file_path+")")
		return None
		
def sync_date_time():	
	global dateTimeSync_py_file_path
	
	cmd = "python3 "+dateTimeSync_py_file_path
	command(cmd)
			
def fill_auth(force = False):	
	global auth_py_file_path, auth_file_path, auth
	
	if force:
		if os.path.isfile(auth_file_path):
			log(INFO, "Delete old auth file")
			os.remove(auth_file_path)
	
		cmd = "python3 "+auth_py_file_path
		command(cmd)
		
	with open(auth_file_path, "r") as a:
		auth = from_json_str(a)
		
	temp = "token" in auth.keys()
	log(INFO, "Auth validation: " + str(temp))
	return temp

def fill_users(force = False):	
	global update_users_list_py_file_path, users_list_path, users
	
	if force:
		if os.path.isfile(users_list_path):
			log(INFO, "Delete old users file")
			os.remove(users_list_path)
	
		cmd = "python3 "+update_users_list_py_file_path
		command(cmd)
		
	with open(users_list_path, "r") as a:
		users = from_json_str(a)
	
	try:
		temp = len(list(users.keys())[0].split(" ")) == 4
		log(INFO, "Users validation: " + str(temp))
		return temp
	except Exception as e:
		log_e(e, "Users validation exception")
		return False
	
def command(cmd):
	return os.popen(cmd).read()
	
def command_async(cmd):
	return os.system(cmd)

	
#Processleri her seferinde durdurmamak için yazıldı. Sadece test methodudur.
def killPyt():
	ps = command("ps -A |grep py")
	psSplit = ps.split(" ")
	if len(psSplit)>12:
		command("kill "+psSplit[1])
