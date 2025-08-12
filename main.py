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

class ElegantVerticalEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane - Elegant Vertical Display")
        
        # DİKEY MONİTÖR İÇİN BOYUTLAR - ZORUNLU DİKEY
        self.setFixedSize(720, 1280)  # Fixed size - zorla dikey
        
        # API anahtarları
        self.api_key = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
        self.weather_api_key = "b0d1be7721b4967d8feb810424bd9b6f"
        self.start_lat = 38.47434762293852
        self.start_lon = 27.112356625119595
        
        self.current_mode = None
        self.video_path = None
        
        # ELEGANT TEMA RENKLERI
        self.colors = {
            'primary': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#e94560',
            'gold': '#ffd700',
            'white': '#ffffff',
            'light_gray': '#f8f9fa',
            'dark_gray': '#2c3e50',
            'glass': 'rgba(255, 255, 255, 0.1)'
        }
        
        self.setup_ui()
        self.setup_video_player()
        self.setup_timers()
        self.switch_to_pharmacy_mode()
        
        # TAM EKRAN MODU - DİKEY
        self.show()  # Normal window önce
        
        print("🎨 Elegant Vertical Pharmacy Monitor başlatıldı!")

    def setup_ui(self):
        # Ana widget stack
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Eczane modu sayfası
        self.pharmacy_widget = QWidget()
        self.setup_pharmacy_ui()
        self.stacked_widget.addWidget(self.pharmacy_widget)
        
        # Video modu sayfası
        self.video_widget = QWidget()
        self.setup_video_ui()
        self.stacked_widget.addWidget(self.video_widget)

    def setup_pharmacy_ui(self):
        """Dikey ekran için optimize edilmiş eczane UI - SCROLL AKTİF"""
        widget = self.pharmacy_widget
        
        # SCROLL AREA EKLE - ZORUNLU SCROLL
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # AsNeeded
        
        # İÇERİK WİDGETİ - YETERLİ YÜKSEK
        content_widget = QWidget()
        content_widget.setMinimumHeight(1400)  # Minimum yükseklik garanti
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)  # Margin artırıldı
        
        # ARKA PLAN
        widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['primary']}, 
                    stop:0.3 {self.colors['secondary']}, 
                    stop:1 {self.colors['primary']});
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['gold']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: transparent;
            }}
        """)
        
        # HEADER KOMPAKT
        self.create_header(layout)
        
        # ECZANE BİLGİLERİ
        self.create_info_section(layout)
        
        # QR + HARİTA YAN YANA
        self.create_qr_map_section(layout)
        
        # FOOTER
        self.create_footer(layout)
        
        # BOŞ ALAN EKLE - SCROLL İÇİN
        spacer = QWidget()
        spacer.setMinimumHeight(100)
        spacer.setStyleSheet("background: transparent;")
        layout.addWidget(spacer)
        
        # Scroll area'ya ekle
        scroll_area.setWidget(content_widget)
        
        # Ana layout
        main_widget_layout = QVBoxLayout(widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.addWidget(scroll_area)

    def create_header(self, layout):
        """Kompakt header - BÜYÜTÜLMÜŞ"""
        header = QWidget()
        header.setFixedHeight(180)  # 140'tan 180'e
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {self.colors['accent']}, 
                stop:0.5 #ff6b6b, 
                stop:1 {self.colors['accent']});
            border-radius: 15px;
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(20)
        
        # SOL: Logo + Başlık
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setSpacing(20)
        
        # Logo - BÜYÜTÜLMÜŞ
        self.logo_label = QLabel()
        self.load_logo()
        self.logo_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: {self.colors['glass']};
            border-radius: 40px;  
            padding: 20px;
            border: 3px solid {self.colors['gold']};
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(80, 80)  # 70'ten 80'e
        left_layout.addWidget(self.logo_label)
        
        # Başlık - BÜYÜTÜLMÜŞ
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(5)
        
        main_title = QLabel("KARŞIYAKA 4")
        main_title.setFont(QFont('Segoe UI', 28, QFont.Bold))  # 24'ten 28'e
        main_title.setStyleSheet(f"color: {self.colors['white']}; background: transparent;")
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("NÖBETÇİ ECZANE")
        sub_title.setFont(QFont('Segoe UI', 18, QFont.Bold))  # 16'dan 18'e
        sub_title.setStyleSheet(f"color: {self.colors['gold']}; background: transparent;")
        title_layout.addWidget(sub_title)
        
        title_widget.setStyleSheet("background: transparent;")
        left_layout.addWidget(title_widget)
        left_widget.setStyleSheet("background: transparent;")
        header_layout.addWidget(left_widget, 2)
        
        # SAĞ: Saat + Hava - BÜYÜTÜLMÜŞ
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        
        # Saat - BÜYÜTÜLMÜŞ
        self.time_label = QLabel()
        self.time_label.setFont(QFont('Consolas', 20, QFont.Bold))  # 16'dan 20'e
        self.time_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: {self.colors['glass']};
            border-radius: 10px;
            padding: 12px 16px;
            border: 2px solid {self.colors['gold']};
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.time_label)
        
        # Hava durumu - BÜYÜTÜLMÜŞ
        weather_widget = QWidget()
        weather_widget.setStyleSheet(f"""
            background: {self.colors['glass']};
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 12px;
        """)
        weather_layout = QHBoxLayout(weather_widget)
        weather_layout.setSpacing(12)
        
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setFont(QFont('Segoe UI', 20, QFont.Bold))  # 16'dan 20'e
        self.weather_temp.setStyleSheet(f"color: {self.colors['gold']}; background: transparent;")
        weather_layout.addWidget(self.weather_temp)
        
        self.weather_desc = QLabel("Yükleniyor...")
        self.weather_desc.setFont(QFont('Segoe UI', 14))  # 10'dan 14'e
        self.weather_desc.setStyleSheet(f"color: {self.colors['white']}; background: transparent;")
        weather_layout.addWidget(self.weather_desc)
        
        right_layout.addWidget(weather_widget)
        right_widget.setStyleSheet("background: transparent;")
        header_layout.addWidget(right_widget, 1)
        
        layout.addWidget(header)
        
        # Saat timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def create_info_section(self, layout):
        """Eczane bilgileri bölümü - KÜÇÜLTÜLMÜŞ"""
        info_container = QWidget()
        info_container.setStyleSheet(f"""
            background: {self.colors['glass']};
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(20, 12, 20, 12)
        info_layout.setSpacing(8)
        
        # Başlık
        title = QLabel("📍 NÖBETÇİ ECZANE BİLGİLERİ")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))  # 18'den 16'ya
        title.setStyleSheet(f"""
            color: {self.colors['gold']};
            background: transparent;
            padding: 6px;
            border-bottom: 2px solid {self.colors['accent']};
        """)
        title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(title)
        
        # İçerik - KÜÇÜLTÜLMÜŞ
        self.info_label = QLabel("Yükleniyor...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Segoe UI', 13))  # 14'ten 13'e
        self.info_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 12px;
            line-height: 1.4;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.info_label.setMinimumHeight(160)  # 200'den 160'a
        self.info_label.setMaximumHeight(180)  # 250'den 180'e
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_container)

    def create_qr_map_section(self, layout):
        """QR + Harita yan yana - KÜÇÜLTÜLMÜŞ"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(12)
        
        # QR Bölümü - KÜÇÜLTÜLMÜŞ
        qr_container = QWidget()
        qr_container.setStyleSheet(f"""
            background: {self.colors['glass']};
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        """)
        
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setContentsMargins(15, 15, 15, 15)
        qr_layout.setSpacing(0)
        
        self.qr_label = QLabel("QR\nYükleniyor...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(150, 150)  # 180'den 150'ye
        self.qr_label.setStyleSheet(f"""
            background: {self.colors['white']};
            border-radius: 10px;
            color: {self.colors['dark_gray']};
            font-size: 12px;
            border: 2px solid {self.colors['gold']};
        """)
        
        qr_center_layout = QHBoxLayout()
        qr_center_layout.addStretch()
        qr_center_layout.addWidget(self.qr_label)
        qr_center_layout.addStretch()
        qr_layout.addLayout(qr_center_layout)
        
        row_layout.addWidget(qr_container, 1)
        
        # Harita Bölümü - KÜÇÜLTÜLMÜŞ
        map_container = QWidget()
        map_container.setStyleSheet(f"""
            background: {self.colors['glass']};
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        """)
        
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(15, 15, 15, 15)
        map_layout.setSpacing(0)
        
        self.map_label = QLabel("Harita yükleniyor...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(150)  # 180'den 150'ye
        self.map_label.setMaximumHeight(170)  # 200'den 170'e
        self.map_label.setStyleSheet(f"""
            background: {self.colors['white']};
            border-radius: 10px;
            color: {self.colors['dark_gray']};
            font-size: 12px;
            border: 2px solid {self.colors['gold']};
        """)
        map_layout.addWidget(self.map_label)
        
        row_layout.addWidget(map_container, 2)
        row_widget.setStyleSheet("background: transparent;")
        layout.addWidget(row_widget)

    def create_footer(self, layout):
        """Kompakt footer"""
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.colors['dark_gray']}, 
                stop:0.5 {self.colors['secondary']}, 
                stop:1 {self.colors['dark_gray']});
            border-radius: 15px;
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        self.last_update_label = QLabel("Son güncelleme: --:--")
        self.last_update_label.setFont(QFont('Segoe UI', 12))
        self.last_update_label.setStyleSheet(f"color: {self.colors['white']}; background: transparent;")
        footer_layout.addWidget(self.last_update_label)
        
        footer_layout.addStretch()
        
        status_label = QLabel("● SİSTEM AKTİF")
        status_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        status_label.setStyleSheet("color: #00ff00; background: transparent;")
        footer_layout.addWidget(status_label)
        
        footer_layout.addStretch()
        
        powered_label = QLabel("Powered by AI")
        powered_label.setFont(QFont('Segoe UI', 10))
        powered_label.setStyleSheet(f"color: {self.colors['white']}; background: transparent;")
        footer_layout.addWidget(powered_label)
        
        layout.addWidget(footer)

    def load_logo(self):
        """Logo yükle"""
        try:
            logo_paths = ["logo/LOGO.png", "logo/logo.png", "logo/Logo.png"]
            logo_loaded = False
            for path in logo_paths:
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        scaled_logo = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_label.setPixmap(scaled_logo)
                        logo_loaded = True
                        print(f"✅ Logo yüklendi: {path}")
                        break
            if not logo_loaded:
                self.logo_label.setText("🏥")
                self.logo_label.setFont(QFont('Segoe UI', 40))
                print("📋 Logo bulunamadı, emoji kullanıldı")
        except Exception as e:
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Segoe UI', 40))
            print(f"⚠️ Logo hatası: {e}")

    def update_time(self):
        """Saat güncelle"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        display_text = f"{time_str}\n{date_str}"
        self.time_label.setText(display_text)

    def setup_video_ui(self):
        """Video UI"""
        widget = self.video_widget
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        widget.setStyleSheet(f"background: {self.colors['primary']};")
        
        self.video_widget_display = QVideoWidget()
        layout.addWidget(self.video_widget_display)
        
        self.no_video_label = QLabel("📺 ads/ klasöründe video bulunamadı")
        self.no_video_label.setAlignment(Qt.AlignCenter)
        self.no_video_label.setFont(QFont('Segoe UI', 32, QFont.Bold))
        self.no_video_label.setStyleSheet(f"""
            background: {self.colors['primary']};
            color: {self.colors['white']};
            padding: 50px;
        """)
        self.no_video_label.hide()
        layout.addWidget(self.no_video_label)

    def setup_video_player(self):
        """Video player kurulum"""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget_display)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.check_video_file()

    def check_video_file(self):
        """Video dosyası kontrol"""
        ads_dir = "ads"
        if not os.path.exists(ads_dir):
            self.video_path = None
            return
        
        for file in os.listdir(ads_dir):
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                self.video_path = os.path.join(ads_dir, file)
                print(f"✅ Video bulundu: {self.video_path}")
                return
        
        self.video_path = None

    def on_media_status_changed(self, status):
        """Video status değişimi"""
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def setup_timers(self):
        """Timer kurulum"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(1800000)  # 30 dakika

    def switch_to_pharmacy_mode(self):
        """Eczane moduna geç"""
        self.current_mode = "pharmacy"
        if hasattr(self, 'media_player') and self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
        self.stacked_widget.setCurrentWidget(self.pharmacy_widget)
        self.fetch_data()
        self.fetch_weather_data()

    def fetch_data(self):
        """Gerçek eczane verisi çek"""
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
                    
                    # Telefon
                    phone = "Bulunamadı"
                    phone_link = parent_div.find('a', href=lambda x: x and 'tel:' in x)
                    if phone_link:
                        phone = phone_link.get('href').replace('tel:', '')
                        if len(phone) == 10:
                            phone = '0' + phone
                    
                    # Adres
                    address = "Adres bulunamadı"
                    address_icon = parent_div.find('i', class_='fa fa-home main-color')
                    if address_icon and address_icon.next_sibling:
                        address = address_icon.next_sibling.strip()
                    
                    # Google Maps
                    maps_link = parent_div.find('a', href=lambda x: x and 'google.com/maps' in x)
                    maps_url = maps_link.get('href') if maps_link else None
                    
                    # Koordinatlar
                    end_lat, end_lon = 38.473137, 27.113438
                    if maps_url and 'q=' in maps_url:
                        try:
                            coords = maps_url.split('q=')[1].split('&')[0]
                            end_lat, end_lon = map(float, coords.split(','))
                        except:
                            pass
                    
                    # Mesafe ve süre
                    distance, duration = self.get_route_info(end_lat, end_lon)
                    
                    # HTML formatında bilgi
                    info_html = f"""
                    <div style='line-height: 1.8; font-size: 16px;'>
                    <p style='color: {self.colors['gold']}; font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 15px;'>
                    ✨ {name} ✨
                    </p>
                    <p style='color: {self.colors['white']}; margin: 10px 0;'>
                    📞 <strong>Tel:</strong> {phone}
                    </p>
                    <p style='color: {self.colors['white']}; margin: 10px 0;'>
                    📍 <strong>Adres:</strong><br>{address}
                    </p>
                    <p style='color: {self.colors['white']}; margin: 10px 0;'>
                    🏢 <strong>Bölge:</strong> KARŞIYAKA 4
                    </p>
                    <hr style='border: 1px solid {self.colors['accent']}; margin: 15px 0;'>
                    <p style='color: {self.colors['gold']}; margin: 10px 0;'>
                    🚗 <strong>Mesafe:</strong> {distance}
                    </p>
                    <p style='color: {self.colors['gold']}; margin: 10px 0;'>
                    ⏱️ <strong>Süre:</strong> {duration}
                    </p>
                    </div>
                    """
                    
                    self.info_label.setText(info_html)
                    
                    # QR kod oluştur
                    if maps_url:
                        self.create_qr_code(maps_url)
                    
                    # Harita oluştur
                    self.create_route_map(end_lat, end_lon)
                    
                    # Son güncelleme
                    now = datetime.now()
                    self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')}")
                    
                    print("✅ Eczane bilgileri güncellendi")
                    return
            
            # Bulunamadı
            self.info_label.setText(f"""
            <div style='text-align: center; color: {self.colors['white']}; font-size: 18px;'>
            <p style='color: {self.colors['accent']}; font-size: 24px; margin-bottom: 20px;'>⚠️</p>
            <p>Bugün KARŞIYAKA 4'te nöbetçi eczane bulunamadı</p>
            </div>
            """)
            
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")
            
        except Exception as e:
            self.info_label.setText(f"""
            <div style='text-align: center; color: {self.colors['accent']}; font-size: 18px;'>
            <p style='font-size: 24px; margin-bottom: 20px;'>❌</p>
            <p>Hata: {str(e)}</p>
            </div>
            """)
            
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Hata)")
            print(f"❌ Güncelleme hatası: {e}")

    def get_route_info(self, end_lat, end_lon):
        """Mesafe ve süre bilgisi al"""
        try:
            directions_url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={self.start_lat},{self.start_lon}&"
                f"destination={end_lat},{end_lon}&"
                f"mode=driving&"
                f"key={self.api_key}"
            )
            
            response = requests.get(directions_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    leg = data['routes'][0]['legs'][0]
                    distance = leg['distance']['text']
                    duration = leg['duration']['text']
                    return distance, duration
                    
        except Exception as e:
            print(f"Rota bilgisi hatası: {e}")
            
        return "~2 km", "~5 dakika"

    def create_route_map(self, end_lat, end_lon):
        """Harita oluştur"""
        try:
            directions_url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={self.start_lat},{self.start_lon}&"
                f"destination={end_lat},{end_lon}&"
                f"mode=driving&"
                f"key={self.api_key}"
            )
            
            directions_response = requests.get(directions_url, timeout=10)
            
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                
                if directions_data['status'] == 'OK':
                    route = directions_data['routes'][0]
                    polyline = route['overview_polyline']['points']
                    
                    # Zoom seviyesi
                    distance_value = route['legs'][0]['distance']['value']
                    if distance_value < 1000:
                        zoom_level = 16
                    elif distance_value < 3000:
                        zoom_level = 15
                    else:
                        zoom_level = 14
                    
                    # Harita boyutları - KÜÇÜLTÜLMÜŞ
                    map_width = 480
                    map_height = 150
                    
                    static_map_url = (
                        f"https://maps.googleapis.com/maps/api/staticmap?"
                        f"size={map_width}x{map_height}&"
                        f"markers=color:green|size:mid|label:K|{self.start_lat},{self.start_lon}&"
                        f"markers=color:red|size:mid|label:E|{end_lat},{end_lon}&"
                        f"path=color:0xe94560|weight:4|enc:{polyline}&"
                        f"zoom={zoom_level}&"
                        f"key={self.api_key}"
                    )
                    
                    # Harita resmini indir
                    map_response = requests.get(static_map_url, timeout=10)
                    
                    if map_response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        
                        scaled_pixmap = pixmap.scaled(480, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.map_label.setPixmap(scaled_pixmap)
                        
                        print("✅ Harita oluşturuldu")
                        return
                        
        except Exception as e:
            print(f"Harita hatası: {e}")
            
        self.map_label.setText("Harita yüklenemedi")

    def fetch_weather_data(self):
        """Hava durumu çek"""
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
            
            self.weather_temp.setText(f"{temp}°C")
            self.weather_desc.setText(desc)
            
            print(f"✅ Hava durumu: {temp}°C - {desc}")
            
        except Exception as e:
            self.weather_temp.setText("--°C")
            self.weather_desc.setText("Hata")
            print(f"Hava durumu hatası: {e}")

    def create_qr_code(self, url):
        """QR kod oluştur"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color=self.colors['primary'], back_color=self.colors['white'])
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
            print("✅ QR kodu oluşturuldu")
            
        except Exception as e:
            self.qr_label.setText(f"QR\nHatası:\n{str(e)}")
            print(f"QR kod hatası: {e}")

    def keyPressEvent(self, event):
        """Klavye olayları"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

if __name__ == "__main__":
    print("🎨 Elegant Vertical Pharmacy Monitor")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    try:
        window = ElegantVerticalEczaneApp()
        print("✅ Pencere oluşturuldu")
        print("📐 Dikey format: 720x1280")
        print("🎨 Elegant tema aktif")
        print("⌨️  ESC: Çıkış, F11: Tam ekran")
        print("🔄 30 dakikada otomatik güncelleme")
        print("=" * 60)
        print("🚀 ÇALIŞIYOR!")
        
        app.exec_()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
