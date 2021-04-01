#0 */2 * * * python3 /var/www/html/send.py &
import os 
import sys
import json
import time
import datetime
import traceback

import RPi.GPIO as GPIO

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)

try:
	def get_id_and_record_token_from_photo(photo):
		try:
			if photo[0:2] == "TN":
				
				temp = photo[2:].split(".")[0]
				temp = temp.split("-")				
				card_id = temp[0]				
				temp = temp[1].split("_")
				dt = temp[0] + "-" + temp[1] + "-" + temp[2] + " " + temp[3] + ":" + temp[4] + ":" + temp[5]
				
				url = get_url_for_rfid_readed(card_id, dt)
				if url == "":
					log(WARNING, "get_id_and_record_token_from_photo by pass")
					return ("", "")
					
				data = http_get(url, j=True)
				if data != None and data["status"] == "success":
					new_name = "ID"+str(data["data"]["user"]["id"])+"_"+data["data"]["user"]["record_token"]+".jpg"
					os.rename(h.base_photo_path + photo, h.base_photo_path + new_name)
					log(INFO, "get_id_and_record_token_from_photo OK")
					
					return (str(data["data"]["user"]["id"]), data["data"]["user"]["record_token"])
					
				else:
					log(WARNING, "get_id_and_record_token_from_photo by pass (data)")
					return ("", "")
				
			elif photo[0:2] == "ID":
				temp = photo.replace(".jpg", "")[2:].split("_")

				return (temp[0], temp[1])
				
		except Exception as e:
			log_e(e, "error in get_id_and_record_token_from_photo")
			return ("", "")
		
	def run():
		log_and_run(fill_auth)
		
		log_and_run(limit_bandwith)
		
		list = os.listdir(h.base_photo_path)
		i = 0
		for photo in list:
			try:
				i = i + 1
				
				if h.loop == False:
					return;
					
				(id, record_token) = log_and_run(get_id_and_record_token_from_photo, photo)
				if id == "":
					continue
					
				url = get_url_for_send_photo()
				
				print(str(i) + " / " + str(len(list)))
				
				params = { "id": id, "record_token": record_token }
				files = {'fotograf[]': open(h.base_photo_path+"ID"+id+"_"+record_token+".jpg", 'rb')}
				
				log_and_run(limit_bandwith)
				data = http_post(url, data = params, files = files, j = True)
				
				if data != None:
					if data["status"] == "success":
						os.remove(h.base_photo_path+"ID"+id+"_"+record_token+".jpg")
					else:
						log(WARNING, "Send file request end with error: " + to_json_str(data)) 
										
			except Exception as e:
				print(e)
				temp = None
		

	#Ana Fonksiyon
	if __name__ == "__main__":	
				
		time.sleep(1)
		
		h.restart = True
		h.loop = True
		
		preload(file_name) 
				
		log_and_run(run)
						
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)