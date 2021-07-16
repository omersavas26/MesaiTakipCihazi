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
	def read_ssh_key():
		data = read_from_file("/root/.ssh/id_rsa.pub")
		if data == None:
			cmd = 'ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""'
			command(cmd)
			data = read_from_file("/root/.ssh/id_rsa.pub")
			
			if data == None:
				return None
			
		return data.strip('\n')
	
	def get_device_unique():
		ssh_key = log_and_run(read_ssh_key)
		params ={ 'ssh_anahtar': ssh_key }
		
		url = log_and_run(get_url_for_deg_device_key)
		data = http_post(url, data=params, j=True)
		if data == None:
			log(ERROR, "Yeni anahtar alinamadi! (data: None, "+to_json_str(params)+")")
			return ""
			
		if data["status"] != "success":
			log(ERROR, "Yeni anahtar alinamadi! (data: "+to_json_str(data)+", params: "+to_json_str(params)+")")
			return ""
			
		key = data["data"]["message"]
		
		macs = log_and_run(get_mac_adresses)		
		serial = log_and_run(get_cpu_serial)
		
		return macs[0] + serial + macs[1] + key
		
	def get_auth():
		global device_table_name
				
		unique = log_and_run(get_device_unique)
		if unique == "": 
			return ""
			
		params = {
			"type": device_table_name,
			"unique": unique
		}
		
		data = http_post(api_base_url+"deviceLogin", data=params, j=True)
		if data == None:
			log(ERROR, "Auth data alinamadi! (data: None, params: "+to_json_str(params)+")")
			return ""
		
		if data["status"] != "success":
			log(ERROR, "Auth data alinamadi! (data: "+to_json_str(data)+", params: "+to_json_str(params)+" )")
			return ""
				
		return data["data"]
		
	def run():
		auth = log_and_run(get_auth)
		if auth != "":						
			data = {
				"token": auth["token"],
				"id": auth["device"]["id"]
			}
			
			try:
				data["name"] = auth["device"]["name"]
			except Exception as e:
				data["name"] = auth["device"]["name_basic"]
						
			write_to_file(h.auth_file_path, data, j = True)
		else:
			log_and_run(add_as_new_device)
			
	def add_as_new_device():
		global api_base_url, new_device_column_set_id
	
		ips = log_and_run(get_ip_adresses)		
		macs = log_and_run(get_mac_adresses)		
		serial = log_and_run(get_cpu_serial)
		unique = log_and_run(get_device_unique)
		real_ip = log_and_run(get_real_ip)
		cihaz_json = read_from_file("/var/www/html/cihaz.json")
		ssh_key = log_and_run(read_ssh_key)
		
		
		detail = {
			"ips": ips,
			"macs": macs,
			"serial": serial,
			"unique": unique,
			"real_ip": real_ip,
			"cihaz_json": cihaz_json,
			"ssh_key": ssh_key
		}
		
		params = {
			"column_set_id": new_device_column_set_id, 
			"detail": to_json_str(detail),
			"id": 0 
		}
		
		url = api_base_url+"public/tables/yeni_cihazlar/store"
		data = http_post(url, data=params, j=True)
		
		if data == None:
			log(ERROR, "Yeni cihaz olarak eklenemedi! (data: None, params: "+to_json_str(params)+")")
			return ""
		
		if data["status"] != "success":
			log(ERROR, "Yeni cihaz olarak eklenemedi! (data: "+to_json_str(data)+", params: "+to_json_str(params)+" )")
			return
		

	
	#Ana Fonksiyon
	if __name__ == "__main__":		
		
		preload(file_name)
		
		log_and_run(run)
				
		log_and_run(endload)


		
except Exception as e:
	fn = os.path.basename(__file__)		
	root_ex(fn, e)