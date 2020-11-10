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

	handler = logging.FileHandler("/var/www/html/guncelle.log")
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)

	logger.addHandler(handler)
	
	
	
	#Degiskenler
	yeniden_baslatma = True
	basladi = False
	debug = False
	oku = True
	base_url = "https://base.url/uploads/2020/01/01/mesaiTakipCihaziGuncellemeAdresi/"
	base_path = "/var/www/html/"
	last_response = None
		
	
	
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
			
		log_yaz(1, "Ayarlar yapildi.")

	def sunucudan_data_getir(url):
		try:
			time.sleep(1)
			
			global last_response
			last_response = None
			
			ctx = ssl.create_default_context()
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE
			
			rr = urllib2.urlopen(url, timeout = 10, context=ctx)			
			last_response = rr.read()
			
			return last_response			
			
		except Exception as e:
			hatayi_log_yaz(e, "Sunucudan data getirilirken hata olustu")
			last_response = None
			
	def hatayi_log_yaz(e, m):
		exc_type, exc_obj, exc_tb = sys.exc_info()	
		log_yaz(3, m +" " + str(e) + " (line: " + str(exc_tb.tb_lineno) + ")")
		
	def versiyon_kontrol():
		global base_url, base_path
		
		if os.path.exists(base_path+"versiyon.txt") == False: 
			return False
			
		v = open(base_path+"versiyon.txt", "r")
		v1 = v.read()
		
		v2 = sunucudan_data_getir(base_url+"versiyon.txt")
		
		return v1 == v2
	
	def guncelle():
		global base_path, base_url
		
		if versiyon_kontrol(): return
		
		dosyalar = sunucudan_data_getir(base_url+"dosyalar.txt")
		for dosya in dosyalar.split("\n"):
			dosya = dosya.replace("\r", "")
			
			log_yaz(1, "Dosya sunucudan getiriliyor: " + dosya)
			txt = sunucudan_data_getir(base_url+dosya)
			
			if txt == None:
				log_yaz(3, "Dosya bulunamadi: " + base_url+dosya)
				continue
			wr = open(base_path+dosya, 'w')
			wr.write(txt)



	#Ana Fonksiyon
	if __name__ == "__main__":
		log_yaz(1, "Basliyor...")
		
		on_yukleme()
		
		basladi = True
		
		guncelle()
		
		log_yaz(1, "Tamamlandi!")


		
except Exception as e:
	
	try:
		log_yaz(1, "Fonksiyon kontrol")
	except Exception as ee:
		def log_yaz(l, s):
			m = "Level: " + str(l) + " - " + str(s)
			print(m)
			with open("/var/www/html/guncelle.log", "a") as f:
				f.write(m)
	
	exc_type, exc_obj, exc_tb = sys.exc_info()	
	log_yaz(3, "Genel hata! " + str(e) + " (line: " + str(exc_tb.tb_lineno) + ")")
	
	if yeniden_baslatma:
		if basladi:
			log_yaz(2, "Uygulama yeniden basliyor")
			os.system("python /var/www/html/guncelle.py") 
		else:
			log_yaz(2, "Hata on yukleme esnasinda olustugu icin yeniden baslatilamaz!")
	else:
		log_yaz(3, "Yeniden baslatilmayacak")