# Mesai Takip Cihazı
## Kütahya İl Özel İdaresi - Bilgi işlem müdürlüğü

![Cihaz](./img/Cihaz.jpg)

Kütahya İl Özel İdaresi için geliştirmiş olduğumuz mesai takip cihazıdır. Yazılımı, devre tasarımı ve (3d yazdırılabilir) kutu tasarımı tamamen bize aittir. Tüm Raspberry Pi sürümleri ile çalışmaktadır. Fakat kutu RP3 için tasarlandığından diğer sürümleri için revizyon gerekir.

Cihazın açılması ile "main.py" yazılımı çalışır ve kart okutulması için beklemeye başlar. Başlatılması esnasında "./auth.py" dosyasını ve "./updateUsersList.py" dosyasını tetikleyerek cihaza özel güncel bir yetki alımasını ve bu yetkiyi kullanarak güncel kullanıcı listesinin alınmasını tetikler. Kullanıcı listesi personelin sunucu iletişimi esnasında bekletilmemesini sağlar. Personel kart okuttuğunda ilk olarak kameradan fotoğrafını alır, sonra ses ve ışık ile sinyal verir. Eğer okutulan kart id numarası "./file/users.json" dosyasında (bkz: "updateUserList.py") kayıtlı ise ekrana personel ismini yazar ver personeli bekletmeden gönderir. Sonra asenkron olarak sunucuya kart okutma bilgisini içeren bir istek atar cevap olarak da bir id numarası bekler. Cevap alabilirse çektiği fotoğrafın adını bu id bilgisi ile değiştirir. Eğer okutulan kart id numarası "./file/users.json" dosyasında yok ise sunucuya senkron bir istek atarak kart okutulma bilgisini gönderir cevap olarak de personel adı ve kart okutma için bir id numarası bekler. Beklediği cevap gelirse çektiği resmin adını yine id numarası ile değiştirerek personel adını ekrana yazdırır. Her ihtimal için; eğer beklenen cevap gelmez ise resmin adını card id ve tarih saat bilgisi olarak bırakır (bkz: "send.py"). Bir sonraki personelin kart okutmasını beklemeye başlar.

Eğer istenir ise, her kart okutmada bir kapı yada turnike tetiklenebilir. Ayrıca sunucu bağlantısı olmadan "./file/users.json" dosyasını manuel olarak doldurarak offline olarak da kullanılabilir.

Cihaz, personel geçişini yavaşlatmamak ve bağlantı olmadığı zamanlarda mesai takibini aksatmamak için çektği fotoğrafları önce hafızasında biriktirir sonra sizin belirlediğiniz peryotlarda sunucuya yüklemeye çalışır (bkz: "send.py"). Fotoğraflar "./foto" dizinindedir. İki tip fotoğraf vardır. İlki; sorunsuz bir şekilde sunucuya kart okutma bilgisi gönderilmiş ve cevap olarak da eklenen kaydın id bilgisi geri dönmüş olan fotoğraflar. Bunların isimleri "ID146589_XXXXX.jpg" şeklindedir. "_" karakterinden sonraki "XXXXXX" dizisi opsiyoneldir. Sunucu tarafından her kayıt için özel bir token gönderilir ise bu "XXXXXX" yerine yazılır. Böylelikle kayıt ikinci bir token ile korunmuş olur. Token bilgisini bilmeyen bir cihaz, fotoğraf yükleme yapamaz. İkinci tip fotoğraflar ise "TN198 76 64 27-2021_04_01_16_58_00.jpg" şeklinde isimlendirilmiştir. Bunlar, kart okutma bilgisi sunucuya gönderilememiş geçişler için çekilmiş olan fotoğraflardır. Adında kart bilgisi ve geçiş zamanını tutar. "send.py" yazılımı belirli peryotlarda çalışarak önce kayıt id 'leri olmayanları sunucuya kart okutma bilgisi oalrak gönderir ve id talep eder; ardından tüm fotoğrafları band genişliğini sınırlandırarak sunucuya yükler.

Sahadaki çok sayıda cihazınızın güncellenmesi için bir mekanizma kurulmuştur. Cihazlar belirli aralıklarda sizin belirdiğiniz adresi kontrol ederek güncel dosyaları otomatik olarak alabilirler (bkz "update.py"). İstenirse bu adres token ile korunabilir. Bu sayede yazılımın yanı sıra font ve logo gibi bilgilerde uzaktan değiştirilebilir.

Cihaz kameranın bir özelliği olarak 135 derece oval fotoğraf almaktadır. Ayrıca yine kameranın bir özelliği olarak karanlık ortamlarda da -gece görüşü- fotoğraf alabilmektedir. 13.56 Mhz mifare rfid kart ile uyumludur.

### auth.py
Eğer token auth ile çalışan bir servisiniz varsa bu dosya çalıştığında servisinize login isteği atar. Login olundu ise token ve cihaz ismi gibi bilgilerden "./file/auth.json" adında bir yetki dosyası oluşturur. "main.py" ve "send.py" gibi dosyalar ilk çalıştıklarında bu dosyayı tetikleyerek auth işlemi gerçekleştirirler ve çalışma süreleri boyunca auth.json dosyasını kullanırlar. Ayrıca cihaz ilk açıldığında da tetiklenir. Eğer cihaz yetkilendirmesi yapmak istenmiyorsa cihaz adı gibi bilgileri içeren sabit bir auth.json dosyası oluşturulabilir.

### clear.py
Cihaz ilk açıldığında çalışarak GPIO pin çıkışlarını temizler.

### control.py
cron ile her dakika çalışarak "main.py" nin çalışıyor olması gibi kontrol edilmesi gereken süreçleri izler. Sorun var ise yeniden başlatır.


### dateTimeSync.py 
Kısıtlı ağlarda cihaz tarih saat servisine erişierek zaman bilgisi alamaz ise bir http servis üzerinden tarih saat bilgisi alınarak cihazın zamanını günceller.


### fileList.txt
Bu dosya güncelleme sunucusu üzerinde bulunur. "update.py" yazılımı önce uzaktaki "version.txt" dosyasına sonra da bu dosyaya bakarak güncellemesi gereken dosyaları belirler ve güncel dosyaları indirerek cihaz üzerinde yazar. Yazılım mekanizmasına yeni bir dosya eklendi ise dosya adı ve yolu fileList.txt içine yazılmalıdır. 

### main.py
Ana yazılımdır. Cihaz ilk açıldığında çalışmaya başlar ve kapanana kadar çalışarak personelin kart okutmasını bekler. Kart okutulması ile fotoğraf çeker ve sunucu bu kart okutulması hakkında bilgilendirir. Başlatılması esnasında "./auth.py" dosyasını ve "./updateUsersList.py" dosyasını tetikleyerek cihaza özel güncel bir yetki alımasını ve (eğer gerekiyorsa) bu yetkiyi kullanarak güncel kullanıcı listesinin alınmasını tetikler.

### send.py
"./main.py" tarafından üretilmiş olan fotoğrafları belirli aralıklara sunucuya yüklemeye çalışır. Başlatılması esnasında "./auth.py" dosyasını tetikler ve (eğer gerekiyorsa) sunucu iletişimi sırasında bu yetki bilgisini kullanır.

### update.py
Belirli aralıklarla güncelleme sunucusuna talepler göndererek gülcel bir sürüm var ise cihaz yazılımını günceller.

### updateUserList.py
Sunucudan güncel kullanıcı bilgisini ister ve "./file/users.json" dosyasını doldurur. İstenirse users.json dosyası manuel olarak doldurularak cihaz offline olarak da kullanılabilir.

### version.txt
Aynı anda hem cihazda hemde güncelleme sunucusunda bulunur. "./update.py" bu dosyaya bakarak, sunucu üzerindeki dosyadan farklı ise güncelleme yapar.

## Bileşenler
 1. Raspberry Pi (3 B+ önerilir)
 2. Mikro SD kart
 3. Raspberry Pi Camera (Raspberry Pi 3 Model B + Night Vision Camera 5MP Wide Angle 135 Degree Fisheye Lens 1080P Camera Module)
 4. PCB Devre
 5. SSD 1306 Oled LCD ekran (128*64)
 6. RFID-RC522 rfid kart okuyucu
 7. Kırmızı ve yeşil kesik baş led
 8. 5V mini usb adaptor ve kablo
 9. Tek kanal 5v röle kartı (Opsiyonel)
 10. 3D yazdırılmış kutu parçaları
 11. Kaplama için yeteri kadar karbon folyo (Opsiyonel)
 12. 4 adet 2.2x6 mm ve 3 adet 2.2x9 mm vida
 13. 13x2, 4x1, 8x1 dişi header 
 14. Buzzer

## Donanım

[Video gelecek]

## Yazılım

1. Image ile kurulum
.img dosyası indirilip micro sd karta "Win32 Disk Imager" yada benzeri bir uygulama ile yazılıp 

2. Manuel kurulum
   - Arduino klasorundeki buzzer.ino dosyası Arduino nanoya upload edilir.
   - Raspbian işletim sistemi sd karta yüklenir ve açılır
   - `sudo raspi-config` ile ayar ekranı açılıp  ssh, camera, i2c ve spi aktifleştirilir
   - Aşağıdaki kurulumlar yapılır.
   
    ```
    sudo apt-get update
    sudo apt-get upgrade

    sudo apt-get install git python3 python3-spidev python3-dev python3-pip python3-smbus  python3-picamera i2c-tools wondershaper libopenjp2-7 -y
	
	sudo python3 -m pip install -U pip
	sudo python3 -m pip install -U setuptools
	
	sudo pip3 install Pillow
	sudo pip3 install adafruit-circuitpython-ssd1306
	sudo pip3 install requests
	
    sudo chmod 777 -R /var/www/html/
	
	git clone https://github.com/lthiery/SPI-Py.git && cd SPI-Py && git checkout 8cce26b9ee6e69eb041e9d5665944b88688fca68 && sudo python3 setup.py install	
    ```
	
   - `sudo crontab -e` ile zamanlanmış görevler açılıp en alta aşağıdaki satırlar eklenir.
   .
    ```	
	@reboot python3 /var/www/html/clear.py &

	@reboot python3 /var/www/html/dateTimeSync.py &
	0 * * * * python3 /var/www/html/dateTimeSync.py &

	@reboot sleep 10 && python3 /var/www/html/main.py

	0 */2 * * * python3 /var/www/html/send.py &

	0 12 * * * python3 /var/www/html/update.py

	0 13 * * * python3 /var/www/html/updateUsersList.py &

	* * * * * python3 /var/www/html/control.py &

	30 22 * * *     /sbin/shutdown -r +1 &
    ```
	
   - wget download.sh && ./download.sh 
   
   
   
   
  
	
	