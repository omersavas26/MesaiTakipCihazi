#@reboot python3 /var/www/html/auth.py &
import os 
import sys
import json
import traceback

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)



try:
	def get_auth():
		return '{"token": "AzqUejyZD4II3n8Wt72d72", "id": 72, "name": "Test Cihazi"}'
		
	def run():
		auth = log_and_run(get_auth)
		
		if auth != "":						
			data = {
				"token": auth["token"],
				"id": auth["device"]["id"], 
				"name": auth["device"]["name"]
			}
						
			write_to_file(h.auth_file_path, data, j = True)
		else:
			log_and_run(add_as_new_device)
			
	def add_as_new_device():
		global api_base_url
	
		print("send request to backend for new device store")
		

	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name)
		
		log_and_run(run)
				
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)