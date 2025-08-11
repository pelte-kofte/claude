import sys
import os
import requests
from bs4 import BeautifulSoup
import qrcode
from io import BytesIO
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class EczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane - Otomatik Sistem")
        self.resize(720, 1000)  # DİKEY FORMAT
        self.api_key = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
        self.weather_api_key = "b0d1be7721b4967d8feb810424bd9b6f"
        self.start_lat = 38.47434762293852  # Kuşdemir Eczanesi
        self.start_lon = 27.112356625119595
        
        # MODE KONTROLÜ
        self.current_mode = None  # "pharmacy" veya "video"
        self.video_path = None
        
        self.setup_ui()
        self.setup_video_player()
        self.setup_timers()
        # self.check_time_mode()  # YORUM: Test için saat kontrolü kapalı
        
        # TEST İÇİN DOĞRUDAN NÖBET MODUNA GEÇ
        self.switch_to_pharmacy_mode()
    
    def setup_ui(self):
        # STACKED WIDGET - İki mod arasında geçiş için
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # ECZANE MODU SAYFASI
        self.pharmacy_widget = QWidget()
        self.setup_pharmacy_ui()
        self.stacked_widget.addWidget(self.pharmacy_widget)
        
        # VİDEO MODU SAYFASI
        self.video_widget = QWidget()
        self.setup_video_ui()
        self.stacked_widget.addWidget(self.video_widget)
    
    def setup_pharmacy_ui(self):
        widget = self.pharmacy_widget
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(15)  # Daha geniş boşluklar
        main_layout.setContentsMargins(15, 15, 15, 15)  # Kenar boşlukları
        
        # ANA ARKA PLAN - PREMIUM DARK
        widget.setStyleSheet("background-color: #0A0E27;")  # Deep navy
        
        # HEADER (BAŞLIK + HAVA DURUMU)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Sol: Başlık - PREMIUM DARK (Fixed)
        title = QLabel("KARŞIYAKA 4 NÖBETÇİ ECZANE")
        title.setFont(QFont('Segoe UI', 22, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setStyleSheet("""
            background-color: #161B33;
            color: #FFFFFF; 
            padding: 20px; 
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
            border: 1px solid #2A3061;
        """)
        header_layout.addWidget(title, 3)
        
        # Sağ: Hava Durumu - PREMIUM DARK (Fixed)
        weather_container = QWidget()
        weather_container.setStyleSheet("""
            background-color: #161B33;
            border-radius: 8px; 
            border: 1px solid #2A3061;
        """)
        weather_layout = QVBoxLayout(weather_container)
        weather_layout.setContentsMargins(16, 14, 16, 14)
        weather_layout.setSpacing(6)
        
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.weather_temp.setAlignment(Qt.AlignCenter)
        self.weather_temp.setStyleSheet("color: #00D4AA; margin: 0; font-weight: 700;")
        weather_layout.addWidget(self.weather_temp)
        
        self.weather_desc = QLabel("Yükleniyor...")
        self.weather_desc.setFont(QFont('Segoe UI', 11))
        self.weather_desc.setAlignment(Qt.AlignCenter)
        self.weather_desc.setStyleSheet("color: #B8C5D6; margin: 0; font-weight: 400;")
        self.weather_desc.setWordWrap(True)
        weather_layout.addWidget(self.weather_desc)
        
        header_layout.addWidget(weather_container, 1)  # 1/4 alan
        
        main_layout.addLayout(header_layout)
        
        # ÜST ALAN: ECZANE BİLGİLERİ + QR KOD
        top_layout = QHBoxLayout()
        
        # Sol: Eczane bilgileri - PREMIUM DARK (Fixed)
        self.info_label = QLabel("Yükleniyor...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Segoe UI', 15))
        self.info_label.setStyleSheet("""
            background-color: #161B33;
            color: #F0F4F8; 
            padding: 26px; 
            border-radius: 8px;
            border: 1px solid #2A3061;
            font-weight: 400;
            line-height: 1.5;
        """)
        self.info_label.setMinimumHeight(300)
        top_layout.addWidget(self.info_label, 2)
        
        # Sağ: QR kod - PREMIUM DARK (Fixed)
        qr_container = QWidget()
        qr_container.setStyleSheet("""
            background-color: #161B33;
            border-radius: 8px;
            border: 1px solid #2A3061;
        """)
        qr_layout = QVBoxLayout(qr_container)
        
        self.qr_label = QLabel("QR\nYükleniyor...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setStyleSheet("""
            color: #B8C5D6; 
            background-color: #0A0E27; 
            border-radius: 6px;
            font-family: 'Segoe UI';
            font-weight: 300;
            border: 1px solid #1A2142;
        """)
        qr_layout.addWidget(self.qr_label)
        
        top_layout.addWidget(qr_container, 1)
        main_layout.addLayout(top_layout)
        
        # ALT ALAN: HARİTA - PREMIUM DARK (Fixed)
        map_container = QWidget()
        map_container.setStyleSheet("""
            background-color: #161B33;
            border-radius: 8px; 
            padding: 16px;
            border: 1px solid #2A3061;
        """)
        map_layout = QVBoxLayout(map_container)
        
        self.map_label = QLabel("Harita yükleniyor...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(470)
        self.map_label.setStyleSheet("""
            background-color: #0A0E27; 
            color: #B8C5D6; 
            border-radius: 6px;
            font-family: 'Segoe UI';
            font-weight: 300;
            border: 1px solid #1A2142;
        """)
        map_layout.addWidget(self.map_label)
        
        main_layout.addWidget(map_container)
        
        # Footer - PREMIUM DARK
        self.last_update_label = QLabel("Son güncelleme: --:--")
        self.last_update_label.setAlignment(Qt.AlignCenter)
        self.last_update_label.setStyleSheet("""
            color: #6B7A94; 
            font-size: 13px; 
            padding: 10px;
            font-family: 'Segoe UI';
            font-weight: 300;
        """)
        main_layout.addWidget(self.last_update_label)
    
    def setup_video_ui(self):
        widget = self.video_widget
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video player
        self.video_widget_display = QVideoWidget()
        layout.addWidget(self.video_widget_display)
        
        # Video bulunamadığında gösterilecek mesaj
        self.no_video_label = QLabel("📺 ads/ klasöründe video bulunamadı")
        self.no_video_label.setAlignment(Qt.AlignCenter)
        self.no_video_label.setFont(QFont('Arial', 24, QFont.Bold))
        self.no_video_label.setStyleSheet("background-color: #2c3e50; color: white;")
        self.no_video_label.hide()
        layout.addWidget(self.no_video_label)
    
    def setup_video_player(self):
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget_display)
        
        # Video bitince başa sar (loop)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        # Video dosyasını kontrol et
        self.check_video_file()
    
    def check_video_file(self):
        """ads/ klasöründe MP4 dosyası var mı kontrol et"""
        ads_dir = "ads"
        if not os.path.exists(ads_dir):
            print("❌ ads/ klasörü bulunamadı")
            self.video_path = None
            return
        
        # .mp4 veya .mov dosyası ara
        for file in os.listdir(ads_dir):
            if file.lower().endswith(('.mp4', '.mov')):
                self.video_path = os.path.join(ads_dir, file)
                print(f"✅ Video bulundu: {self.video_path}")
                return
        
        print("❌ ads/ klasöründe MP4/MOV dosyası bulunamadı")
        self.video_path = None
    
    def on_media_status_changed(self, status):
        """Video bitince başa sar"""
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
            print("🔄 Video başa sarıldı")
    
    def setup_timers(self):
        # SAAT KONTROLÜ - Her 1 dakika (YORUM: Test için kapalı)
        # self.time_check_timer = QTimer()
        # self.time_check_timer.timeout.connect(self.check_time_mode)
        # self.time_check_timer.start(60000)  # 1 dakika = 60000ms
        # print("⏰ Saat kontrol timer başlatıldı (1 dakika)")
        
        # ECZANE BİLGİ GÜNCELLEMESİ - Her 30 dakika
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(1800000)  # 30 dakika = 1800000ms
        print("🔄 Güncelleme timer başlatıldı (30 dakika)")
    
    def check_time_mode(self):
        """Saate göre mod kontrol et"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        current_time = f"{current_hour:02d}:{current_minute:02d}"
        
        # 18:45-08:45 arası NÖBET MODU (gece boyunca)
        # 08:45-18:45 arası VİDEO MODU (gündüz)
        
        is_night_mode = False
        
        if current_hour > 18 or (current_hour == 18 and current_minute >= 45):
            is_night_mode = True  # 18:45'ten sonra
        elif current_hour < 8 or (current_hour == 8 and current_minute < 45):
            is_night_mode = True  # 08:45'ten önce
        
        if is_night_mode:
            # NÖBET MODU
            if self.current_mode != "pharmacy":
                print(f"🏥 NÖBET MODUNA GEÇİŞ - Saat: {current_time}")
                self.switch_to_pharmacy_mode()
        else:
            # VİDEO MODU
            if self.current_mode != "video":
                print(f"📺 VİDEO MODUNA GEÇİŞ - Saat: {current_time}")
                self.switch_to_video_mode()
    
    def switch_to_pharmacy_mode(self):
        """Nöbetçi eczane moduna geç"""
        self.current_mode = "pharmacy"
        
        # Video durdur
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
        
        # Eczane sayfasını göster
        self.stacked_widget.setCurrentWidget(self.pharmacy_widget)
        
        # Eczane bilgilerini güncelle
        self.fetch_data()
        
        print("✅ Nöbetçi eczane modu aktif")
    
    def switch_to_video_mode(self):
        """Video moduna geç"""
        self.current_mode = "video"
        
        # Video dosyasını tekrar kontrol et
        self.check_video_file()
        
        if self.video_path and os.path.exists(self.video_path):
            # Video sayfasını göster
            self.stacked_widget.setCurrentWidget(self.video_widget)
            
            # Video gizle, player göster
            self.no_video_label.hide()
            self.video_widget_display.show()
            
            # Video oynat
            media_content = QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.video_path)))
            self.media_player.setMedia(media_content)
            self.media_player.play()
            
            print(f"✅ Video modu aktif: {self.video_path}")
        else:
            # Video bulunamadı mesajı göster
            self.stacked_widget.setCurrentWidget(self.video_widget)
            self.video_widget_display.hide()
            self.no_video_label.show()
            
            print("❌ Video modu: dosya bulunamadı")
    
    def fetch_data(self):
        """Eczane bilgilerini çek ve güncelle"""
        try:
            print("📡 Eczane bilgileri güncelleniyor...")
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            h4_elements = soup.find_all('h4', class_='red')
            
            for h4 in h4_elements:
                strong = h4.find('strong')
                if strong and 'KARŞIYAKA 4' in strong.text.upper():
                    name = strong.text.strip()
                    
                    parent_div = h4.parent
                    
                    # Telefon bul
                    phone = "Bulunamadı"
                    phone_link = parent_div.find('a', href=lambda x: x and 'tel:' in x)
                    if phone_link:
                        phone = phone_link.get('href').replace('tel:', '')
                        if len(phone) == 10:
                            phone = '0' + phone
                    
                    # Adres bul
                    address = "Adres bulunamadı"
                    address_icon = parent_div.find('i', class_='fa fa-home main-color')
                    if address_icon and address_icon.next_sibling:
                        address = address_icon.next_sibling.strip()
                    
                    # Google Maps linki bul
                    maps_link = parent_div.find('a', href=lambda x: x and 'google.com/maps' in x)
                    maps_url = maps_link.get('href') if maps_link else None
                    
                    # Koordinatları çıkar
                    end_lat, end_lon = 38.473137, 27.113438  # Varsayılan
                    if maps_url and 'q=' in maps_url:
                        try:
                            coords = maps_url.split('q=')[1].split('&')[0]
                            end_lat, end_lon = map(float, coords.split(','))
                        except:
                            pass
                    
                    # Bilgileri göster (TESLA STYLE - CLEAN)
                    info_text = f"""{name}
                    
Tel: {phone}

Adres: {address}

Bölge: KARŞIYAKA 4"""
                    
                    self.info_label.setText(info_text)
                    
                    # QR kod oluştur
                    if maps_url:
                        self.create_qr_code(maps_url)
                    
                    # HARİTA oluştur
                    self.create_route_map(end_lat, end_lon)
                    
                    # HAVA DURUMU çek
                    self.fetch_weather_data()
                    
                    # Son güncelleme zamanını güncelle
                    now = datetime.now()
                    self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')}")
                    
                    print("✅ Eczane bilgileri güncellendi")
                    return
            
            self.info_label.setText("❌ Bugün KARŞIYAKA 4'te nöbetçi eczane bulunamadı")
            self.fetch_weather_data()  # Hava durumunu yine de çek
            
            # Son güncelleme zamanını güncelle
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")
            
        except Exception as e:
            self.info_label.setText(f"Hata: {str(e)}")
            self.fetch_weather_data()  # Hava durumunu yine de çek
            
            # Son güncelleme zamanını güncelle
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Hata)")
            
            print(f"❌ Güncelleme hatası: {e}")
    
    def fetch_weather_data(self):
        try:
            print("🌡️ Hava durumu alınıyor...")
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': 'Izmir,TR',
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].title()
            
            # PREMIUM DARK renk paleti - neon accents
            if temp < 5:
                temp_color = "#4FC3F7"  # Light Blue
            elif temp < 15:
                temp_color = "#00D4AA"  # Neon Green
            elif temp < 25:
                temp_color = "#F0F4F8"  # Clean White
            elif temp < 35:
                temp_color = "#FFB74D"  # Warm Orange
            else:
                temp_color = "#FF6B35"  # Neon Orange (hot)
            
            self.weather_temp.setText(f"{temp}°C")
            self.weather_temp.setStyleSheet(f"color: {temp_color}; margin: 0; font-weight: 700; font-family: 'Segoe UI';")
            self.weather_desc.setText(f"{desc}")
            
            print(f"✅ Hava durumu: {temp}°C - {desc}")
            
        except Exception as e:
            self.weather_temp.setText("--°C")
            self.weather_desc.setText("Hata")
            print(f"Hava durumu hatası: {e}")
    
    def create_qr_code(self, url):
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='black', back_color='white')
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.qr_label.setText(f"QR Hatası:\n{str(e)}")
    
    def create_route_map(self, end_lat, end_lon):
        try:
            # ÖNCE DIRECTIONS API'DEN GERÇEK ROTA AL
            directions_api_url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={self.start_lat},{self.start_lon}&"
                f"destination={end_lat},{end_lon}&"
                f"mode=driving&"
                f"key={self.api_key}"
            )
            
            print("🛣️ Gerçek yol tarifi alınıyor...")
            directions_response = requests.get(directions_api_url, timeout=10)
            
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                
                if directions_data['status'] == 'OK':
                    # Encoded polyline'ı al
                    route = directions_data['routes'][0]
                    polyline = route['overview_polyline']['points']
                    
                    # Mesafe ve süre bilgisi al
                    leg = route['legs'][0]
                    distance = leg['distance']['text']
                    duration = leg['duration']['text']
                    distance_value = leg['distance']['value']  # metre cinsinden
                    
                    # DİNAMİK ZOOM - Mesafeye göre ayarla
                    if distance_value < 1000:  # 1km'den az
                        zoom_level = 16
                    elif distance_value < 3000:  # 1-3km arası
                        zoom_level = 15
                    else:  # 3km'den fazla
                        zoom_level = 14
                    
                    print(f"📏 Mesafe: {distance} ({distance_value}m)")
                    print(f"🔍 Zoom seviyesi: {zoom_level}")
                    
                    # DİKEY EKRAN İÇİN HARİTA BOYUTU
                    map_width = 700
                    map_height = 400
                    
                    # STATIC MAP'e polyline ekle (NEON GREEN PATH)
                    static_map_url = (
                        f"https://maps.googleapis.com/maps/api/staticmap?"
                        f"size={map_width}x{map_height}&"
                        f"markers=color:green|size:mid|label:●|{self.start_lat},{self.start_lon}&"
                        f"markers=color:red|size:mid|label:E|{end_lat},{end_lon}&"
                        f"path=color:0x00D4AA|weight:4|enc:{polyline}&"
                        f"zoom={zoom_level}&"
                        f"style=feature:all|element:all|saturation:-20|lightness:-30&"
                        f"key={self.api_key}"
                    )
                    
                    print(f"📍 Başlangıç: Kuşdemir Eczanesi")
                    print(f"🏥 Bitiş: {end_lat},{end_lon}")
                    print(f"🛣️ Gerçek rota çiziliyor...")
                    
                    # Harita resmini indir
                    map_response = requests.get(static_map_url, timeout=10)
                    
                    if map_response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        
                        # Dikey ekrana uygun boyutlandır
                        scaled_pixmap = pixmap.scaled(680, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.map_label.setPixmap(scaled_pixmap)
                        
                        print(f"✅ Gerçek yol tarifi yüklendi!")
                        print(f"⏱️ Süre: {duration}")
                        
                        # Info label'a mesafe/süre ekle
                        current_text = self.info_label.text()
                        updated_text = current_text + f"\n\nMesafe: {distance}\nTahmini süre: {duration}"
                        self.info_label.setText(updated_text)
                        
                    else:
                        self.map_label.setText(f"❌ Harita yüklenemedi\nHTTP: {map_response.status_code}")
                else:
                    self.map_label.setText(f"❌ Rota bulunamadı: {directions_data['status']}")
            else:
                self.map_label.setText(f"❌ Directions API hatası: {directions_response.status_code}")
                
        except Exception as e:
            self.map_label.setText(f"❌ Harita hatası:\n{str(e)}")
            print(f"Harita hatası: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EczaneApp()
    window.show()
    app.exec_()
