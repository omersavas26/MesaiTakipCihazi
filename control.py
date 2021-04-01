#* * * * * python3 /var/www/html/control.py &
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
	def start_main():
		log(INFO, "main calistir")
		cmd = "python3 "+h.app_base_path+"main.py &"
		command_async(cmd)
		
	def control_main():
		temp = command("ps -aux | grep  python | grep main.py")
		log(INFO, "ps list: " + temp)
				
		if temp == None or temp == "":
			log(ERROR, "ps list alinamadi")
				
		control = False
		temp = temp.split("\n")
		for i in range(len(temp)):
			if len(temp[i]) == 0:
				continue
				
			try:
				log(INFO, "index: " + str(temp[i].index(h.app_base_path+"main.py")))
				control = True
			except Exception as e:
				t = None
				
		if control == False:
			log_and_run(start_main)
		
	def run():
		log_and_run(control_main)
				
	
	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name, online = False)
						
		log_and_run(run)
								
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)
