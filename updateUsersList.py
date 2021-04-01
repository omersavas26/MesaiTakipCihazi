#0 13 * * * python3 /var/www/html/updateUsersList.py &
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
	def run():
		log_and_run(fill_auth)
		url = log_and_run(get_url_for_users_list)
		if url == "":
			log(ERROR, "url is None!")
			return
			
		data = http_get(url, j=True, force = True)
		if data == None:
			log(ERROR, "data is None!")
			return
			
		write_to_file(h.users_list_path, data["data"], j = True)
		
		

	#Ana Fonksiyon
	if __name__ == "__main__":	
		
		preload(file_name, online = False) 
				
		log_and_run(run)
						
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)