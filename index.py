import RPi.GPIO as GPIO
import MFRC522
import signal
import calendar
import time
from time import sleep
import smbus
import ssl
import socket
import fcntl
import struct
import datetime
import threading
import urllib
import urllib2
import sys
#import json
import picamera
import logging
import netifaces as ni
import os 
import string
import random as rn
from random import *
import pika
import paho.mqtt.client as paho

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


try:
	
	#Log Ayarlama
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	handler = logging.FileHandler("/var/www/html/kartligiris.log")
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	handler.setFormatter(formatter)

	logger.addHandler(handler)
	
	disp = Adafruit_SSD1306.SSD1306_128_64(rst=0)
	
	
	#Degiskenler
	mqtt_broker = "192.168.0.71"
	mqtt_subject_saglik = None
	log_random = rn.random()
	yeniden_baslatma = True
	basladi = False
	oku = True
	debug = True
	son_kesme = [0 for x in range(20)]
	url = "http://sunucu/ana/url/"
	son_id = ""
	foto_yol = "/var/www/html/foto/"
	ekran_zaman_asimi = 2
	lcd_temp = ["" for x in range(10)]
	lcd_x = ["" for x in range(10)]
	lcd_y = ["" for x in range(10)]
	lcd_f = ["" for x in range(10)]
	bilgi = -1
	mu_sifirla = False;
	led_basla = 0
	mesaj_ttl = 3
	r = ["", "", ""]
	buzzer = 4 #buzzer = 7  //7. bacak GPIO4
	kirmizi_led = 23#kirmizi_led = 16
	yesil_led = 24#yesil_led = 18
	kapi = 17#kapi = 11
	son_ip = None
	
	
	#Nesneler
	MIFAREReader = MFRC522.MFRC522()
	bus = smbus.SMBus(1)
	camera = picamera.PiCamera()
	ni.ifaddresses('eth0') 
	rabbitConnection = None
	rabbitChannel = None
	mqtt_client = None

	

	#Fonksiyonlar
	def asenkron_calistir(f, a = [], t = 0):
		log_yaz(1, "Asenkron calisacak :" + str(f))
		
		i = threading.Thread(target=f, args = a)
		i.start()
		
		if float(t) > 0.0:
			log_yaz(1, "Asenkron islem beklenecek :" + str(t))
			i.join(float(t))
				
		log_yaz(1, "Asenkron islem yada beklenme suresi bitti")

	def mqqt_konu_tanimla():
		global mqtt_subject_saglik
		mqtt_subject_saglik = "kubis/"+IP()+"/saglik/"
		
	def mqtt_baslat():
		try:
			global mqtt_broker, mqtt_client, mqtt_subject_saglik
			mqtt_client = paho.Client(IP())
			mqtt_client.connect(mqtt_broker)
			mqqt_konu_tanimla()
		except Exception, ee:
			log_yaz(1, "Mqqt baslatilamadi: " + str(ee))
		
		
	def mqtt_mesaj(s, m):
		try:
			global mqtt_client
			mqtt_client.publish(s, m)
			log_yaz(1, "Mqtt mesaj: " + str(s) + " --- " + str(m))
		except Exception, ee:
			log_yaz(1, "Mqqt mesaj paylasilamadi: " + str(ee) + " - Mesaj: " + str(s) +  " --- " + str(m))
		
	def rabbit_baslat():
		try:
			global rabbitConnection, rabbitChannel
			rabbitConnection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.71'))
			rabbitChannel = rabbitConnection.channel()
			rabbitChannel.queue_declare(queue='logs')
		except Exception, ee:
			log_yaz(1, "Rabbitmq baslatilamadi: " + str(ee))
	
	def rabbit_mesaj(m):
		try:
			global rabbitChannel
			rabbitChannel.basic_publish(exchange='', routing_key='logs', body=m)
			log_yaz(1, "Rabbit mesaj: " + str(m))
		except Exception, ee:
			log_yaz(1, "Rabbitmq mesaj gonderilemedi: " + str(ee) + " - Mesaj: " + m)

	def log_yaz(l, s):
		#l => 1: info, 2:warning, 3:error
		if l == 1:
			if debug:
				logger.info('%s', str(s))
				print "LOG -> level:" + str(l) + " - " + str(s)
		else:
			global log_random
			print "LOG -> level:" + str(l) + " - " + str(s)
			m = '{ "kaynak":"MesaiCihazi", "kaynak_ip":"'+IP()+'", "log_random":"'+str(log_random)+'", "description":"'+str(s)+'"}'
			asenkron_calistir(rabbit_mesaj, [m])
		
	def ip_yenile():
		log_yaz(1, "IP yenileniyor")
		os.system("systemctl restart dhcpcd")  
		log_yaz(1, "IP yenilendi")
		mqqt_konu_tanimla()
		
	def ip_degisti():
		asenkron_calistir(mqtt_baslat)
		asenkron_calistir(rabbit_baslat)

	def IP():
		try:
			global son_ip
			log_yaz(1, "IP istendi")
			ipTemp = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
			log_yaz(1, "IP: " + ipTemp)
			if son_ip != ipTemp:
				log_yaz(1, "IP degisti")
				son_ip = ipTemp
				ip_degisti()
			return ipTemp
		except Exception, e:
			log_yaz(1, "IP alinamadi: " + str(e))
			if kesme_fark(5) > 60000:
				log_yaz(1, "IP yenilenecek")
				kesme_zaman_tut(5)
				ip_yenileme = threading.Thread(target=ip_yenile)
				ip_yenileme.start()
			return ""

	def cikis(signal,frame):
		log_yaz(1, "Program kapaniyor...")
		global oku
		oku = False

		GPIO.cleanup()
		log_yaz(1, "aeo")


	def kesme_fark(k):
		return son_kesme[0] - son_kesme[k]

	def kesme_zaman_tut(k):
		son_kesme[k] = son_kesme[0]



	def lcd_temp_sifirla():
		ii = 0;
		
		lcd_x[ii] = 0;
		lcd_y[ii] = 0;
		lcd_f[ii] = 12;
		lcd_temp[ii] = IP();
		ii = ii + 1
		
		lcd_x[ii] = 0;
		lcd_y[ii] = 20;
		lcd_f[ii] = 18;
		lcd_temp[ii] = "    Kutahya Il Ozel Idaresi - Bilgi Islem Mudurlugu";
		ii = ii + 1
		
		lcd_x[ii] = 0;
		lcd_y[ii] = 51;
		lcd_f[ii] = 12;
		lcd_temp[ii] = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"));
		ii = ii + 1

	def logo_yaz():
		image = Image.open('/var/www/html/img/logo.png').convert('1')
		disp.image(image)
		disp.display()
	
	def ekran_guncelle():  
		#log_yaz(1, "Ekran guncelleme yapilacak")
		global bilgi
		
		if bilgi == 2:
			logo_yaz()
		else: 
			width = disp.width
			height = disp.height
			image = Image.new('1', (width, height))

			# Get drawing object to draw on image.
			draw = ImageDraw.Draw(image)
			
			for i in range(len(lcd_temp)):
				if len(lcd_temp[i]) == 0:
					continue

				ws = (128 / (lcd_f[i] / 2)) + 2

				if len(lcd_temp[i]) > ws:
					#lcd_temp[i] = lcd_temp[i][1:] + lcd_temp[i][0:1]
					temp_m = lcd_temp[i]
					lcd_x[i] = lcd_x[i] - 5
				else:
					temp_m = lcd_temp[i].strip()
					
				font = ImageFont.truetype("/var/www/html/font/lato.ttf", lcd_f[i])
				draw.text((lcd_x[i], lcd_y[i]), temp_m, font=font, fill=255)
				
			disp.image(image)
			disp.display()
					
		#log_yaz(1, "Ekran guncelleme yapildi")
		
	def bilgi_guncelle():
		global bilgi
		
		lcd_temp_sifirla()
		
		log_yaz(1, "Bilgi guncellenecek. bilgi: " + str(bilgi))
		
		if bilgi > 2:
			bilgi = 0
			
		lcd_x[1] = 0

		if bilgi == 0:
			lcd_temp[1] = "    Kamerali mesai kontrol cihazi";
		elif bilgi == 1:
			lcd_temp[1] = "    Kutahya Il Ozel Idaresi - Bilgi Islem Mudurlugu";

		bilgi += 1
		
	def zaman_kesmesi():
		#log_yaz(1, "Zaman kesmesi")  
		
		if datetime.datetime.now().minute == 00 and datetime.datetime.now().hour== 22:
			log_yaz(1, "Rutin kapatma")
			global oku
			oku = False
		 
		global mu_sifirla
		
		if kesme_fark(1) > 50:
			kesme_zaman_tut(1)
			ekran_guncelle()
			
		if mu_sifirla:
			if kesme_fark(6) > 1000 * ekran_zaman_asimi:
				mu_sifirla = False
				lcd_temp_sifirla()
		
		if mu_sifirla == False:
			if kesme_fark(2) > 15000:
				kesme_zaman_tut(2)
				bilgi_guncelle()
		
		if kesme_fark(7) > 60000:
			kesme_zaman_tut(7)
			asenkron_calistir(mqtt_mesaj, [mqtt_subject_saglik, "1"])
		
		#log_yaz(1, "Zaman kesmesi sonu")  

	def on_yukleme():
		log_yaz(1, "Ayarlar yapiliyor...")
		
		log_yaz(1, "LCD Baslatiliyor")
		disp.begin()
		disp.clear()
		disp.display()
		logo_yaz()
		log_yaz(1, "LCD Baslatildi")

		log_yaz(1, "Cikislar ayarlaniyor")
		
		GPIO.setwarnings(False)
		
		GPIO.setup(buzzer, GPIO.OUT)
		GPIO.setup(kirmizi_led, GPIO.OUT)
		GPIO.setup(yesil_led, GPIO.OUT)
		GPIO.setup(kapi, GPIO.OUT)

		GPIO.output(buzzer, 0)
		GPIO.output(kirmizi_led, 0)
		GPIO.output(yesil_led, 0)
		GPIO.output(kapi, 0)
		
		signal.signal(signal.SIGINT, cikis)
		
		lcd_temp_sifirla()

		camera.rotation = 90
		
		log_yaz(1, "Cikislar ayarlandi")
		
		asenkron_calistir(rabbit_baslat)

		log_yaz(1, "Rabbit ayarlandi")
		
		asenkron_calistir(mqtt_baslat)
		
		log_yaz(1, "Mqtt ayarlandi")
		
	#def ses_cal_async(f, s):
	def ses_cal(f, s):
		global buzzer
		st = int(f * s)
		za = int((1.0 / f) * 1000000)
		t = datetime.datetime.now().microsecond
		s = False 

		for x in range(0, st):
			temp = datetime.datetime.now().microsecond - t
			if temp < 0:
				temp += 1000000

			while temp < za:
				i = 0
				temp = datetime.datetime.now().microsecond - t
				if temp < 0:
					temp += 1000000

			GPIO.output(buzzer, s)
			s = not s
			t = datetime.datetime.now().microsecond
			
		GPIO.output(buzzer, False)

	#def ses_cal(f, s):
		#ses_cal_async(f, s)
		#cal = threading.Thread(target=ses_cal_async, args = (f, s))
		#cal.start()
		#cal.join()
		
	def ekran_bilgi_degistir(s):
		global bilgi
		global mu_sifirla
		
		bilgi = 0;
		mu_sifirla = True
		lcd_temp[1] = "    "+s;
		lcd_x[1] = 0
		
		kesme_zaman_tut(6)

	def uyari(s):
		ekran_bilgi_degistir(s)
		ekran_guncelle()
		
		ses_cal(400, 0.12)
		"""ses_cal(410, 0.2)
		time.sleep(0.1)
		ses_cal(380, 0.2)"""

	def mesaj(s):
		ekran_bilgi_degistir(s)
		ekran_guncelle()
		
		ses_cal(1000, 0.12)
		#time.sleep(0.03)
		#ses_cal(1100, 0.08)
		"""ses_cal(450, 0.1)
		time.sleep(0.05)
		ses_cal(450, 0.1)"""
	
	def bekleyin():
		ekran_bilgi_degistir("Bekleyin...")
		ekran_guncelle()

	def sunucu(u):
		try:
			global r
			r = ["","",""]
			
			ctx = ssl.create_default_context()
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE
			
			rr = urllib2.urlopen(url + u, timeout = 1, context=ctx)
			rr = rr.read()
			rr = rr.replace('{', '').replace('}', '').split(",") 
			for t in rr:
				t = t.replace('"', '').split(':')
				r[int(t[0])] = t[1] 
			
		except Exception, e:
			log_yaz(1, "Personel adi sunucudan alinirken hata olustu! " + str(e))
			r = ["","",""]

	def kart_okundu(fn, id):		
		log_yaz(1, "Kart okundu: " + id)
		
		global r
		
		ip = IP()
		#Tetiklenecek adres
		u = "api/card_id/"+id.replace(" ", "%20")+"|"+ip
		cal = threading.Thread(target=sunucu, args = (u, ))
		cal.start()
		cal.join(1)#Timeout 1
		
		if r == ["","",""]:
			tanimsiz_kart(fn, id)
		else:
			if r[0] == "OK":
				if len(r[1]) > 0: 
					mesaj(r[1])
				else:
					mesaj(id)
		
				os.rename(foto_yol + fn, foto_yol + "ID"+str(r[2])+".jpg")
			else:
				tanimsiz_kart(fn, id)
				
		r = ["","",""]

	def tanimsiz_kart(fn, id):
		mesaj(id)
		os.rename(foto_yol + fn, foto_yol + "TN"+id+"-"+str(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))+".jpg")

	def foto_cek():		
		log_yaz(1, "Fotograf cekiliyor")
		
		min_char = 8
		max_char = 12
		allchar = string.ascii_letters + string.digits
		name = "".join(choice(allchar) for x in range(randint(min_char, max_char))) + ".jpg"
		
		camera.capture(foto_yol + name)
		
		log_yaz(1, "Fotograf cekildi")
		
		return name
	
	def yesil_led_yak():
		global led_basla
		
		led_basla = time.time()
		GPIO.output(yesil_led, 1)
		
	def yesil_led_sondur(b):
		global led_basla
		if b:
			if (time.time() - led_basla) < 1:
				time.sleep(1 - (time.time() - led_basla))
				
		GPIO.output(yesil_led, 0)
		
	def kirmizi_led_yak():
		global led_basla
		
		led_basla = time.time()
		GPIO.output(kirmizi_led, 1)
		
	def kirmizi_led_sondur(b):
		global led_basla
		
		if b:
			time.sleep(1 - (time.time() - led_basla))
			
		GPIO.output(kirmizi_led, 0)
		
	def kapi_ac():
		global kapi
		for x in range(0, 3):
			GPIO.output(kapi, 1)
			time.sleep(0.3)
			GPIO.output(kapi, 0)
			time.sleep(0.3)
		

	#Ana Fonksiyon
	if __name__ == "__main__":
		log_yaz(1, "Basliyor...")
		
		on_yukleme()
		
		basladi = True
				
		while oku:
			#time.sleep(0.1)
			millis = int(time.time() * 1000)
			if son_kesme[0] != millis:
				son_kesme[0] = millis
				zaman_kesmesi()

			if kesme_fark(3) > 1000:
				(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
				if status == MIFAREReader.MI_OK:

					(status,uid) = MIFAREReader.MFRC522_Anticoll()

					if status == MIFAREReader.MI_OK:
						yesil_led_yak()
						bekleyin()
						
						kapi_ac_thread = threading.Thread(target=kapi_ac)
						kapi_ac_thread.start()
						
						kesme_zaman_tut(3)
						temp_id = str(uid[0]) + " " + str(uid[1]) + " " + str(uid[2]) + " " + str(uid[3])

						if temp_id == son_id and kesme_fark(4) < 60000:
							yesil_led_sondur(False)
							kirmizi_led_yak()
							uyari("Bu kart az once okutuldu!")
							kirmizi_led_sondur(True)
						else: 
							fn = foto_cek()
							
							son_id = temp_id
							kesme_zaman_tut(4)
							
							kart_okundu(fn, son_id)
							yesil_led_sondur(True)
							
except Exception, e:
	
	try:
		log_yaz(1, "Fonksiyon kontrol")
	except Exception, ee:
		def log_yaz(l, s):
			m = "Level: " + str(l) + " - " + str(s)
			print m
			with open("/var/www/html/kartligiris.log", "a") as f:
				f.write(m)
	
	exc_type, exc_obj, exc_tb = sys.exc_info()	
	log_yaz(3, "Genel hata! " + str(e) + " (line: " + str(exc_tb.tb_lineno) + ")")
	
	if yeniden_baslatma:
		if basladi:
			log_yaz(2, "Uygulama yeniden basliyor")
			camera.close()
			os.system("python /var/www/html/index.py") 
		else:
			log_yaz(2, "Hata on yukleme esnasinda olustugu icin yeniden baslatilamaz!")
	else:
		log_yaz(3, "Yeniden baslatilmayacak")
	
	GPIO.cleanup()
	try:
		rabbitConnection.close()
	except Exception, ee:
		print ""