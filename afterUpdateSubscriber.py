import os 
import sys
import json
import time
import traceback

sys.path.append("/var/www/html/lib/")
from helper import *
import helper as h

file_name = os.path.basename(__file__)

try:
	def file_update(file_name):
		txt = http_get(h.update_base_url+file_name)
		write_to_file(h.app_base_path+file_name, txt)
		log(INFO, file_name+" upgrade OK")
		
	def version_file_update():
		version_file = "version.txt"
		log_and_run(file_update, version_file)	
		
	def update_file_update():
		update_file = "update.py"
		log_and_run(file_update, update_file)	
		
	def run():
		log_and_run(version_file_update)
		log_and_run(update_file_update)
	
	
	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name)
						
		log_and_run(run)
								
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)