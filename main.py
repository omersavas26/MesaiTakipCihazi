##@reboot sleep 10 && python3 /var/www/html/main.py & 
##2021-07-16 12:00:00

import os 
import sys
import time
import datetime
import traceback

import RPi.GPIO as GPIO

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)



buzzer_pin = 4 #buzzer_pin = 7  //7. bacak GPIO4
red_led = 23#red_led = 16
green_led = 24#green_led = 18
triger_pin = 17#triger_pin = 11

display_scene_timer_period = 15.0
display_using = False
current_scene = -1
scenes = []

read_rfid_timer_period = 0.25	
local_last_rfid_card_id = ""

last_rfid_card_id_remember_timeout = 75.0
local_debug = False

sendPhotoForever = False

tanimsiz_kullanici_ad = "Tan\u0131ms\u0131z"
tanimsiz_kullanici_soyad = "Kullan\u0131c\u0131"

try:
	def clear_pins():
		global buzzer_pin, red_led, green_led, triger_pin
		
		pin_off(buzzer_pin)
		pin_off(red_led)
		pin_off(green_led)
		pin_off(triger_pin)
		
	def on_load():
		log_and_run(write_logo_on_display)
		
		log_and_run(clear_pins)
		
		log_and_run(set_cam)		
		
		temp = log_and_run(fill_auth, True)
		if temp == True:
			temp = log_and_run(fill_users, True)
		else:
			log_and_run(fill_users)
		
		if temp == False:
			log(INFO, "Users or Auth was failed")
			h.connected = False
		else:		
			h.connected = True
			
		log_and_run(connection_control)
		
		log_and_run(fill_scene)
		
	def set_cam():
		h.camera.rotation = 90
		h.camera.resolution = (1024, 768)
		
	def fill_scene():
		global scenes
		
		scenes.append(scene_1)
		scenes.append(scene_2)
		scenes.append(scene_3)
		scenes.append(logo_scene)
		
	def logo_scene():
		global current_scene, display_using
		control_index = 3
		seq = -1
		
		while True:
			if h.loop == False:
				break;
				
			if current_scene != control_index:
				break;
			
			waited = False 
			
			while display_using:
				log(INFO, "Display using.")
				waited = True
				time.sleep(1)
			
			if waited:
				log_and_run(clear_display)
			
			if seq != h.display_clear_seq:
				seq = h.display_clear_seq
				
				log_and_run(write_logo_on_display)
			
			time.sleep(0.3)
		
		
	def get_now_info_for_display():
		now = datetime.datetime.now()
			
		temp = str(now.strftime("%d aaa %H:%M:%S"));
		temp = temp.replace("aaa", h.months[now.month-1])
		
		temp = temp.split(" ")
		
		d = temp[0]+" "+temp[1]
		t = temp[2]
		return (d, t)
		
	def place_holder_date_time(params = None):
		
		if params == None:
			(d, t) = log_and_run(get_now_info_for_display)
			params = {
				"d": d,
				"t": t
			}
		
		write_text_on_display(params["d"], font_size = 16)
		write_text_on_display(params["t"], x=87, font_size = 16)
		
		return params
		
		
		
	def place_holder_auth_name(params = None):		
		if params == None:
		
			if h.auth == None:
				text = "Yetkisiz Cihaz - Yetkisiz Cihaz ";
			else:
				text = h.auth["name"] + " - " + h.auth["name"]
			
			params = {
				"sizes": [0, 0, 0, 0],
				"text": text,
				"current_x": 10
			}
			
		clean_area_on_display(params["sizes"])
		params["sizes"] = write_text_on_display(params["text"], x = params["current_x"], y = 22, font_size = 36)
		
		params["current_x"] = params["current_x"] - 7
		
		return params		
		
		
	def scene_1(current_x = 10):	
		scene_base(0, False, place_holder_date_time, place_holder_auth_name, 0.05)
		
	def get_real_local_ip():
		ips = get_ip_adresses()
		
		ip = "-"
		for i in range(len(ips)):
			if ips[i].find("127.0") > -1:
				continue
				
			ip = ips[i]
			break
			
		return ip
				
	def place_holder_no_connection(params = None):
		global oled_data
				
		ip = log_and_run(get_real_local_ip) 
		
		write_text_on_display("Internet", x = 18, y = 0, font_size = 24)
		write_text_on_display("Yok", x=42, y=25, font_size = 22)		
		write_text_on_center_of_display(ip, y = 48, font_size = 16)
	
	def scene_2():	
		scene_base(1, h.connected, place_holder_no_connection)
		
	def place_holder_no_auth(params = None):
		write_text_on_display("Yetkisiz", x = 10, y = 5, font_size = 28)
		write_text_on_display("Cihaz", x=25, y=32, font_size = 28)

	def scene_3():		
		scene_base(2, h.auth != None, place_holder_no_auth)
		
		
	def scene_base(control_index, next_scene_control, writing_function_on_clear, writing_function_forewer = None, loop_period = 0.3):
		global current_scene, display_using, local_debug
		
		if next_scene_control:
			current_scene = current_scene + 1
			if current_scene == len(scenes):
				current_scene = 0
				
			log_and_run_async(scenes[current_scene])	
			return
		
		seq = -1
				
		h.debug = False
		params1 = None
		params2 = None
		while True:
			if h.loop == False:
				break;
				
			if current_scene != control_index:
				break;
			
			waited = False 
			
			while display_using:
				log(INFO, "Display using")
				waited = True
				time.sleep(1)
			
			if waited:
				log_and_run(clear_display)
			
			if seq != h.display_clear_seq:
				seq = h.display_clear_seq
				
				params1 = log_and_run(writing_function_on_clear, params1)
				
			if writing_function_forewer != None:
				params2 = log_and_run(writing_function_forewer, params2)
			
			time.sleep(loop_period)
			
		h.debug = local_debug
			
	def run():
		log_and_run_async(update_display_scene)
		
		log_and_run(read_rfid)
		
	def update_display_scene():
		global display_scene_timer_period, current_scene, scenes, display_using
		
		temp = threading.Timer(display_scene_timer_period, update_display_scene)
		temp.daemon = True
		temp.start()
				
		current_scene = current_scene + 1
		if current_scene == len(scenes):
			current_scene = 0
				
		try:
			while display_using:
				log(INFO, "Display using..")
				time.sleep(0.3)
				
			log_and_run(clear_display)
			log_and_run(scenes[current_scene])
		except Exception as e:
			log_e(e, "update_display_scene error")
				
	def wait_message():
		log_and_run(clear_display)
		write_text_on_display("Bekleyin...", x=0, y=22, font_size = 26)
		
	def show_rfid_same_card_message_on_display():
		global red_led, display_using
		
		display_using = True		
		time.sleep(0.3)
		
		pin_on(red_led, time_out = 1)		
		pin_on(buzzer_pin, time_out = 0.05)
		
		log_and_run(clear_display)
				
		write_text_on_display("Bu kart", x = 24, y = 0, font_size = 22)
		write_text_on_display("az once", x = 24, y = 21, font_size = 22)
		write_text_on_display("okutldu!", x = 20, y = 42, font_size = 22)
		
		time.sleep(1)
		
		display_using = False

	def show_ip_on_display():
		global display_using 
		
		display_using = True
		time.sleep(0.3)
		
		ip = log_and_run(get_real_local_ip) 
		log_and_run(clear_display)
		write_text_on_center_of_display(ip, font_size = 16, direction = "xy")
		time.sleep(5);
		
		display_using = False
		
	def toggle_send_photo_forever():
		global sendPhotoForever, display_using
		
		display_using = True
		time.sleep(0.3)
		
		log_and_run(clear_display)
		
		if sendPhotoForever:
			write_text_on_center_of_display("Hemen aktar iptal", font_size = 16, direction = "xy")
			sendPhotoForever = False
		else:
			write_text_on_center_of_display("Hemen aktar acik", font_size = 16, direction = "xy")
			sendPhotoForever = True
		
		time.sleep(3)
		display_using = False
		
	def send_photo(file):
		global display_using
		
		temp = file.replace(".jpg", "")[2:].split("_")
		id = temp[0]
		record_token = temp[1]
		
		url = get_url_for_send_photo()
				
		params = { "id": id, "record_token": record_token }
		files = {'fotograf[]': open(h.base_photo_path+file, 'rb')}
		
		data = http_post(url, data = params, files = files, j = True)
		
		if data != None:
			if data["status"] == "success":
				os.remove(h.base_photo_path+file)
				display_message("Hemen aktar ok", time_out=3)	
			else:
				display_message("Hemen aktar hata.", time_out=3)				
		else:
			display_message("Hemen aktar hata", time_out=3)		
			
	def display_message(msg, time_out = 1):
		global display_using
		
		log(INFO, "Display msg: " + msg) 
		
		display_using = True
		time.sleep(0.3)
		
		log_and_run(clear_display)
		write_text_on_center_of_display(msg, font_size = 16, direction = "xy")
		time.sleep(time_out)
		display_using = False
				
	def same_rfid_read():
		global display_using
							
		if h.rfid_same_count == 4:
			log(INFO, "show_ip_on_display will start")
			log_and_run(show_ip_on_display)
		if h.rfid_same_count == 6:
			log(INFO, "toggle_send_photo_forever will start")
			log_and_run(toggle_send_photo_forever)
		elif h.rfid_same_count == 8:
			display_using = False
			log_and_run(reboot_os)
			return			
			
	def rfid_readed_request_async(card_id, photo_name):
		global sendPhotoForever
		
		url = get_url_for_rfid_readed(card_id)
		if url == "":
			log(WARNING, "rfid_readed_request_async by pass")
			return
			
		data = http_get(url, j=True)
		if data != None and data["status"] == "success":
			new_name = "ID"+str(data["data"]["user"]["id"])+"_"+data["data"]["user"]["record_token"]+".jpg"
			os.rename(h.base_photo_path + photo_name, h.base_photo_path + new_name)
			log(INFO, "rfid_readed_request_async OK")
			
			if sendPhotoForever:
				log_and_run(send_photo, new_name)
			
		else:
			log(WARNING, "rfid_readed_request_async by pass (data)")
			
	def rfid_readed_request(params):
		global sendPhotoForever, tanimsiz_kullanici_ad, tanimsiz_kullanici_soyad
				
		try:
			url = get_url_for_rfid_readed(params["card_id"])
			if url == "":
				log(WARNING, "rfid_readed_request by pass")
				return (tanimsiz_kullanici_ad, tanimsiz_kullanici_soyad)
				
			log_and_run(unlimit_bandwith)
			data = http_get(url, j=True)
			if data != None and data["status"] == "success":
				new_name = "ID"+str(data["data"]["user"]["id"])+"_"+data["data"]["user"]["record_token"]+".jpg"
				os.rename(h.base_photo_path + params["photo_name"], h.base_photo_path + new_name)
				
				if sendPhotoForever:
					log_and_run_async(send_photo, [new_name])
				
				log(INFO, "rfid_readed_request OK")
				
				if data["data"]["user"]["name"] == None:
					data["data"]["user"]["name"] = tanimsiz_kullanici_ad
					data["data"]["user"]["surname"] = tanimsiz_kullanici_soyad
					
				return (data["data"]["user"]["name"], data["data"]["user"]["surname"])
				
			else:
				log(WARNING, "rfid_readed_request by pass (data)")
				return (t, k)
				
		except Exception as e:
			log_e(e, "read_rfid rfid_readed_request")
			return (t, k)
			
	def clear_local_last_rfid_card_id():
		global local_last_rfid_card_id, local_debug
		
		temp = h.debug
		if local_debug:
			h.debug = True
		
		log(INFO, "clear_local_last_rfid_card_id running...")
		local_last_rfid_card_id = ""
		log(INFO, "clear_local_last_rfid_card_id OK")
		
		if local_debug:
			h.debug = temp
				
	def read_rfid():
		global green_led, display_using, read_rfid_timer_period, local_last_rfid_card_id, local_debug, same_rfid_read_control, last_rfid_card_id_remember_timeout, rfid_read_mode_async, relay_only_true_user, tanimsiz_kullanici_ad, tanimsiz_kullanici_soyad
		
		while True:
			if h.loop == False: break
			
			try:	
				card_id = get_card_id_from_rfid()
				if card_id != None:
					
					h.debug = local_debug
										
					now = str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
					photo_name = "TN"+card_id+"-"+now+".jpg"
					log_and_run_async(take_photo, [photo_name])
					
					display_using = True
					
					if local_last_rfid_card_id == card_id:
						log_and_run(same_rfid_read)
						
						
					if same_rfid_read_control and local_last_rfid_card_id == card_id:
						log_and_run(show_rfid_same_card_message_on_display)
					else:	
						if relay_only_true_user == False:
							pin_on(green_led, 1)
						
						local_last_rfid_card_id = card_id
						
						temp = threading.Timer(last_rfid_card_id_remember_timeout, clear_local_last_rfid_card_id)
						temp.daemon = True
						temp.start()						
						
						if relay_only_true_user == False:
							pin_on(buzzer_pin, time_out = 0.05)
							pin_on(triger_pin, time_out = 0.05)
						
						if rfid_read_mode_async and card_id in h.users:						
							log_and_run_async(rfid_readed_request_async, [card_id, photo_name])	
							name = h.users[card_id]["name"]
							surname = h.users[card_id]["surname"]
						else:
							log_and_run(wait_message)
							
							(name, surname) = log_and_run(rfid_readed_request, {"card_id": card_id, "photo_name": photo_name})
							
							if name != tanimsiz_kullanici_ad and surname != tanimsiz_kullanici_soyad and relay_only_true_user:
								pin_on(green_led, 1)
								pin_on(buzzer_pin, time_out = 0.05)
								pin_on(triger_pin, time_out = 0.05)
							elif rfid_read_mode_async == False:
								pin_on(red_led, 1)
							
						log_and_run(clear_display)
						
						write_text_on_center_of_display(name, y = 2, font_size = 20)
						write_text_on_center_of_display(surname, y = 25, font_size = 20)
						
						temp = str(datetime.datetime.now().strftime("%H:%M"))
						write_text_on_center_of_display(temp, y = 45, font_size = 20)
						
						time.sleep(1)
											
					display_using = False
					h.debug = False

			except Exception as e:
				display_using = False
				log_e(e, "read_rfid error")
			
			time.sleep(read_rfid_timer_period)
		
		

	#Ana Fonksiyon
	if __name__ == "__main__":	
				
		time.sleep(1)
		
		h.restart = True
		h.loop = True
		h.debug = local_debug;
		
		pin_config = {"in": [], "out": [buzzer_pin, red_led, green_led, triger_pin]}
		
		preload(file_name, online = False, disp = "oled", cam = True, rf = True, pins = pin_config) 
		
		log_and_run(on_load)
		
		log_and_run(run)
						
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)