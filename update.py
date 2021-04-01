#0 12 * * * python3 /var/www/html/update.py &
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
	def version_control():
		version_file = "version.txt"
		
		if os.path.exists(h.app_base_path+version_file) == False:
			return False
			
		local_version = log_and_run(read_from_file, h.app_base_path+version_file)
		remote_version = http_get(h.update_base_url+version_file)
		
		return local_version == remote_version
		
	def run():
		log_and_run(unlimit_bandwith)
		
		if log_and_run(version_control): return
		
		files = http_get(h.update_base_url+"fileList.txt")
		for file in files.split("\n"):
			file = file.replace("\r", "")
			
			if len(file) == 0: continue
			
			temp = file.split(".")
			ext = temp[-1]
			
			url = h.update_base_url+file
			path = h.app_base_path+file
			
			if ext == "py" or ext == "txt":			
				log(INFO, "File read from server: " + file)
				txt = http_get(url)
				
				if txt == None:
					log(WARNING, "File not found: " + path)
					return
					
				log(INFO, "File write to local: " + path)
				write_to_file(path, txt)
			else:
				if download_file(url, path, sllDisable = True) == False:
					log(WARNING, "wget error")
					return
			
		cmd = "python3 "+h.after_update_subs_py_file_path
		command(cmd)
	
	
	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name)
						
		if h.connected:
			log_and_run(run)
		else:
			log(ERROR, "Connected false")
								
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)