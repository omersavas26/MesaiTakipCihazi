import signal
import sys
import logging
import os 
import ssl
import urllib2
import json
import time
import requests



try:
	
	#Log Ayarlama
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	handler = logging.FileHandler("/var/www/html/aktar.log")
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)

	logger.addHandler(handler)
	
	
	
	#Degiskenler
	yeniden_baslatma = True
	basladi = False
	debug = False
	oku = True
	base_url = "https://base.url/api/v1/"
	foto_yol = "/var/www/html/foto/"
	last_response = None
	token = "public"
	
	rfidCihazId = 1
	anahtar = "anahtar"
	
	
	
	#Fonksiyonlar
	def log_yaz(l, s):
		#l => 1: info, 2:warning, 3:error
		if l == 1:
			if debug:
				_log_yaz(l, s)
		else:
			_log_yaz(l, s)
			
	def _log_yaz(l, s):
		logger.info('%s', str(s))
		print("LOG -> level:" + str(l) + " - " + str(s))

	def cikis(signal,frame):
		global oku
		oku = False
		log_yaz(1, "Program kapaniyor...")

	def on_yukleme():
		log_yaz(1, "Ayarlar yapiliyor...")
		
		os.system("wondershaper eth0 200 200")
		
		requests.packages.urllib3.disable_warnings() 
		
		signal.signal(signal.SIGINT, cikis)	
		
		global rfidCihazId, anahtar
		data = {}
		with open('/var/www/html/cihaz.json', 'r') as cihaz:
			data = json.load(cihaz)
			rfidCihazId = data["rfidCihazId"]
			anahtar = data["anahtar"]
			
		log_yaz(1, "Ayarlar yapildi.")

	def sunucuya_resim_upload_yap_ve_json_data_getir(id, resim):
		try:
			time.sleep(1)
			
			global last_response, foto_yol, base_url, token
			
			last_response = None
			
			files = {'fotograf[]': open(foto_yol+resim, 'rb')}
			data = { 'column_set_id': '108', 'fotograf_old': '[]', 'id': id }

			url = base_url + token + "/tables/kullanci_rfid_gecisler/"+str(id)+"/update"
			rt = requests.post(url, files=files, data=data, verify=False)
			
			last_response = rt.json()
			
			return last_response			
			
		except Exception as e:
			hatayi_log_yaz(e, "Sunucuya resim upload yapilirken hata olustu")
			last_response = None
		
	def sunucudan_json_data_getir(url):
		try:
			time.sleep(1)
			
			global last_response
			last_response = None
			
			ctx = ssl.create_default_context()
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE
			
			rr = urllib2.urlopen(url, timeout = 10, context=ctx)			
			last_response = json.load(rr) 
			
			return last_response			
			
		except Exception as e:
			hatayi_log_yaz(e, "Sunucudan json data getirilirken hata olustu")
			last_response = None
			
	def hatayi_log_yaz(e, m):
		exc_type, exc_obj, exc_tb = sys.exc_info()	
		log_yaz(3, m +" " + str(e) + " (line: " + str(exc_tb.tb_lineno) + ")")
	
			
	def resim_adindan_id_ve_gecis_zamani_getir(resim):
		try:
			resim = resim.replace("**", "")
			resim = resim.replace("--", "")
			resim = resim.replace("__", "")
			resim = resim.replace(".jpg", "")
			
			resim = resim[2:]
			
			id = resim.split("-")[0]
			temp = resim.split("-")[1].split("_")
			gecis_zamani = temp[0] + "-" + temp[1] + "-" + temp[2] + " " + temp[3] + ":" + temp[4] + ":00"
			
			return [id, gecis_zamani]	
			
		except Exception as e:
			hatayi_log_yaz(e, "Resim adindan id ve geciz zamani getirilirken hata olustu!")
			
	def resim_adindan_id_talep_url_getir(resim):
		try:
			if resim[0:2] == "TN":
				dizi = resim_adindan_id_ve_gecis_zamani_getir(resim)
				if dizi == None: return
					
				global rfidCihazId, anahtar
					
				url = '/tables/kullanci_rfid_gecisler/store?';
				url += 'personel_id=&fotograf=&dosyalar=&rfid_cihaz_id='+str(rfidCihazId);
				url += '&gecis_zamani='+dizi[1].replace(" ", "%20")+'&state=1&column_set_id=9&anahtar='+anahtar+'&kart_id='+dizi[0].replace(" ", "%20");
				url += '&disable_rfid_time_control=1';
				
				return url
				
		except Exception as e:
			hatayi_log_yaz(e, "Resim adindan id talep url getiriliken hata olustu!")
			
	def resim_adindan_id_getir(resim):
		try:
			if resim[0:2] == "TN":
				url = resim_adindan_id_talep_url_getir(resim)
				if url == None: return
				
				global base_url, token
				data = sunucudan_json_data_getir(base_url+token+url)
				return data["user"]["id"]
				
			elif resim[0:2] == "ID":
				return resim.replace(".jpg", "")[2:]
				
		except Exception as e:
			hatayi_log_yaz(e, "Resim adindan id getiriliken hata olustu!")
	
	def aktar():
		global foto_yol, oku
		
		for resim in os.listdir(foto_yol):
			if os.path.isfile(os.path.join(foto_yol, resim)):
				try:
					if oku == False:
						return
						
					id = resim_adindan_id_getir(resim)
					if id == None:
						log_yaz(3, "Resim adindan id alinamadi: " + resim)
						continue
					
					os.rename(os.path.join(foto_yol, resim), os.path.join(foto_yol, "ID"+str(id)+".jpg"))
					resim = "ID"+str(id)+".jpg"
					
					rt = sunucuya_resim_upload_yap_ve_json_data_getir(id, resim)
					
					if rt["data"]["message"] == "success":
						log_yaz(1, "Yuklendi: " + resim)
						os.remove(os.path.join(foto_yol, resim))
					
				except Exception as e:
					hatayi_log_yaz(e, "Resim aktarilirken hata olustu!")



	#Ana Fonksiyon
	if __name__ == "__main__":
		log_yaz(1, "Basliyor...")
		
		on_yukleme()
		
		basladi = True
		
		aktar()
		
		log_yaz(1, "Tamamlandi!")


		
except Exception as e:
	
	try:
		log_yaz(1, "Fonksiyon kontrol")
	except Exception as ee:
		def log_yaz(l, s):
			m = "Level: " + str(l) + " - " + str(s)
			print(m)
			with open("/var/www/html/aktar.log", "a") as f:
				f.write(m)
	
	exc_type, exc_obj, exc_tb = sys.exc_info()	
	log_yaz(3, "Genel hata! " + str(e) + " (line: " + str(exc_tb.tb_lineno) + ")")
	
	if yeniden_baslatma:
		if basladi:
			log_yaz(2, "Uygulama yeniden basliyor")
			os.system("python /var/www/html/aktar.py") 
		else:
			log_yaz(2, "Hata on yukleme esnasinda olustugu icin yeniden baslatilamaz!")
	else:
		log_yaz(3, "Yeniden baslatilmayacak")