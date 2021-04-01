#0 * * * * python3 /var/www/html/dateTimeSync.py &
#@reboot python3 /var/www/html/dateTimeSync.py &
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
	def run():
		global api_base_url
				
		data = http_get(api_base_url+"dateTime", j=True)
		if data == None:
			log(ERROR, "Tarih saat alinamadi! (data: None)")
			return 
			
		if data["status"] != "success":
			log(ERROR, "Tarih saat alinamadi! (data:"+to_json_str(data)+")")
			return
			
		temp = data["data"]["message"].split(" ")
		
		temp[0] = temp[0].replace("-", "")
		cmd = "date +%Y%m%d -s \""+temp[0]+"\""
		
		rt = log_and_run(command, cmd)
		rt = rt.strip('\n')
		if rt != temp[0]:
			log(ERROR, "Tarih ayarlanamiyor (rt:"+rt+", temp[0]:"+temp[0]+")")
		
		cmd = "date +%T -s \""+temp[1]+"\""
		rt = log_and_run(command, cmd).strip('\n')
		if rt != temp[1]:
			log(ERROR, "Saat ayarlanamiyor (rt:"+rt+", temp[1]:"+temp[1]+")")
	
	
	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name)
						
		log_and_run(run)
								
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)