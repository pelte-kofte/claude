import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QStackedLayout, QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QDesktopServices, QPixmap, QPainter, QPainterPath, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QUrl, QTimer, QTime, QSize, QRectF

from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import time
import unicodedata
import os
from io import BytesIO 
from urllib.parse import quote_plus

from PIL import Image
import qrcode

# --- API KEYS VE AYARLAR ---
GOOGLE_MAPS_API_KEY = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE" 
OPENWEATHER_API_KEY = "b0d1be7721b4967d8feb810424bd9b6f" 
OPENWEATHER_CITY = "Izmir"
OPENWEATHER_LANG = "tr"
OPENWEATHER_UNITS = "metric"

# Eczane Kusdemir koordinatları (başlangıç noktası)
ECZANE_KUSDEMIR_LAT = 38.47422 
ECZANE_KUSDEMIR_LON = 27.11251

# Nominatim Geocoder
geolocator = Nominatim(user_agent="eczane_nobet_uygulamasi_vitrin")

# --- YARDIMCI FONKSİYONLAR ---
def extract_coords_from_map_url(url):
    """Google Maps URL'sinden koordinat çıkar"""
    # ?q=lat,lng formatı
    match_q = re.search(r'\?q=(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match_q:
        lat = float(match_q.group(1))
        lon = float(match_q.group(2))
        print(f"DEBUG: Koordinatlar '?q=' formatından çıkarıldı: Lat={lat}, Lon={lon}")
        return lat, lon

    # @lat,lng formatı
    match_at = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match_at:
        lat = float(match_at.group(1))
        lon = float(match_at.group(2))
        print(f"DEBUG: Koordinatlar '@' formatından çıkarıldı: Lat={lat}, Lon={lon}")
        return lat, lon
        
    print(f"DEBUG: Harita URL'sinden koordinat çıkarılamadı: {url}")
    return None, None

def get_driving_route_polyline(origin_lat, origin_lon, dest_lat, dest_lon, api_key):
    """Google Directions API ile rota polyline'ı al"""
    directions_url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={origin_lat},{origin_lon}&"
        f"destination={dest_lat},{dest_lon}&"
        f"mode=driving&"
        f"key={api_key}"
    )
    
    try:
        response = requests.get(directions_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK' and data['routes']:
            encoded_polyline = data['routes'][0]['overview_polyline']['points']
            print(f"DEBUG: Directions API'den rota polyline başarıyla alındı.")
            return encoded_polyline
        else:
            print(f"Directions API hatası: {data.get('error_message', data['status'])}")
            return None
    except Exception as e:
        print(f"Directions API hatası: {e}")
        return None

def get_coordinates_from_address(address, region_fallback=None):
    """Adres için Nominatim ile koordinat al"""
    address_attempts = [address]
    if region_fallback and region_fallback != "Bilinmiyor":
        address_attempts.append(f"{address}, {region_fallback}, İzmir, Türkiye")
        if "KARŞIYAKA" in region_fallback.upper():
            address_attempts.append(f"{address}, Karşıyaka, İzmir, Türkiye")
        address_attempts.append(f"{address}, İzmir, Türkiye")

    # Adres temizleme
    simplified_address = re.sub(r'\bNO:\s*\d+[/\s\w]*\b', '', address, flags=re.IGNORECASE).strip()
    simplified_address = re.sub(r'\s*\(.*\)$', '', simplified_address).strip()

    if simplified_address != address and simplified_address:
        address_attempts.append(f"{simplified_address}, İzmir, Türkiye")
    
    # Unique attempts
    seen = set()
    unique_attempts = []
    for item in address_attempts:
        if item not in seen:
            seen.add(item)
            unique_attempts.append(item)

    for attempt_address in unique_attempts:
        time.sleep(0.5)
        try:
            print(f"DEBUG: Nominatim ile adres denemesi: '{attempt_address}'")
            location = geolocator.geocode(attempt_address, timeout=10)
            if location:
                print(f"DEBUG: Nominatim'den koordinatlar alındı: Lat={location.latitude}, Lon={location.longitude}")
                return {"lat": location.latitude, "lon": location.longitude}
        except Exception as e:
            print(f"DEBUG: Nominatim hatası: {e}")
            time.sleep(1)

    print(f"DEBUG: Nominatim ile koordinat bulunamadı: '{address}'")
    return {"lat": None, "lon": None}

def fetch_and_process_data(url="https://www.izmireczaciodasi.org.tr/nobetci-eczaneler", target_bolge="KARŞIYAKA 4"):
    """Eczane verilerini çek ve işle"""
    print("🔍 Veri güncelleniyor...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Website çekilemedi: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    all_eczane_elements = soup.find_all('div', class_='col_12_of_12')

    if not all_eczane_elements:
        print("❌ Eczane elementleri bulunamadı")
        return None

    filtered_eczane_data = []

    for i, element in enumerate(all_eczane_elements):
        eczane_name = "Unknown"
        eczane_region = "Unknown"
        address_full_text = "Adres bulunamadı"
        phone = "Telefon bulunamadı"
        map_url = "Harita bulunamadı"
        coordinates = {"lat": None, "lon": None}

        # Eczane adı ve bölge parse et
        name_element = element.find('h4', class_='red')
        if name_element and name_element.find('strong'):
            full_name_and_bolge = name_element.find('strong').text.strip()
            name_region_match = re.search(r'^(.*?)\s*-\s*(.+)$', full_name_and_bolge)
            if name_region_match:
                eczane_name = name_region_match.group(1).strip()
                eczane_region = name_region_match.group(2).upper().strip()
            else:
                eczane_name = full_name_and_bolge
                region_match_fallback = re.search(r'(KARŞIYAKA\s*\d+|BUCA\s*\d+|BORNOVA\s*\d+|ALİAĞA|ÇİĞLİ\s*\d+|\bİZMİR\b)', 
                                                 full_name_and_bolge, re.IGNORECASE)
                if region_match_fallback:
                    eczane_region = region_match_fallback.group(0).upper().strip()

        # Bölge filtresi
        if target_bolge and eczane_region != target_bolge:
            continue

        # Adres, telefon ve harita bilgileri
        p_tag = element.find('p')
        if p_tag:
            full_p_html = str(p_tag)
            
            # Adres çıkar
            address_match = re.search(r'<i class=\'fa fa-home main-color\'></i>\s*(.*?)(?=<br\s*/>\s*<i class=\'fa fa-(arrow-right|phone|map-marker|print) main-color\'></i>|$)', 
                                    full_p_html, re.DOTALL)
            if address_match:
                address_full_text = address_match.group(1).strip()
                address_full_text = address_full_text.replace('<br />', ' ').replace('<br/>', ' ').strip()
                address_full_text = re.sub(r'\s+', ' ', address_full_text).strip()
            else:
                first_text_node = next((s for s in p_tag.contents if isinstance(s, str) and s.strip()), None)
                if first_text_node:
                    address_full_text = first_text_node.strip()
                    address_full_text = re.sub(r'\s+', ' ', address_full_text).strip()

            # Telefon çıkar
            phone_link = p_tag.find('a', href=re.compile(r'tel:'))
            if phone_link:
                phone = phone_link.text.strip()
            else:
                phone_match_fallback = re.search(r'(\b0?\d{10}\b|\b\d{7}\b)', p_tag.get_text(strip=True))
                if phone_match_fallback:
                    phone = phone_match_fallback.group(0)

            # Harita URL çıkar
            map_link_element = p_tag.find('a', title=re.compile(r'Harita Konumu', re.IGNORECASE))
            if map_link_element:
                map_url = map_link_element['href'].strip()
            else:
                map_link_element_alt = p_tag.find('a', string=re.compile(r'Eczaneyi haritada görüntülemek için tıklayınız', re.IGNORECASE))
                if map_link_element_alt:
                    map_url = map_link_element_alt['href'].strip()

        print(f"\n--- Eczane: {eczane_name} ({eczane_region}) ---")
        print(f"📍 Adres: '{address_full_text}'")
        print(f"🗺️ Harita URL: '{map_url}'")

        # Koordinat çıkar
        if map_url != "Harita bulunamadı":
            lat, lon = extract_coords_from_map_url(map_url)
            if lat is not None and lon is not None:
                coordinates = {"lat": lat, "lon": lon}
        
        # Nominatim ile koordinat al
        if coordinates["lat"] is None and address_full_text != "Adres bulunamadı":
            print(f"🌍 Nominatim ile koordinat deneniyor...")
            nominatim_coords = get_coordinates_from_address(address_full_text, eczane_region)
            if nominatim_coords["lat"] is not None:
                coordinates = nominatim_coords

        filtered_eczane_data.append({
            'name': eczane_name,
            'address': address_full_text,
            'phone': phone,
            'region': eczane_region,
            'map_url': map_url,
            'coordinates': coordinates
        })
        print(f"✅ Koordinatlar: {coordinates}")
    
    return filtered_eczane_data

# --- ANA EKRAN SINIFI ---
class NobetciEczaneScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_display_region = "KARŞIYAKA 4"
        self.all_pharmacies = []
        self.init_ui_screen()
        self.load_data()
        self.fetch_weather_data()

        # Timer'lar
        self.data_refresh_timer = QTimer(self)
        self.data_refresh_timer.timeout.connect(self.load_data)
        self.data_refresh_timer.start(3600000)  # 1 saat

        self.time_update_timer = QTimer(self)
        self.time_update_timer.timeout.connect(self.update_time_label)
        self.time_update_timer.start(1000)  # 1 saniye

        self.weather_update_timer = QTimer(self)
        self.weather_update_timer.timeout.connect(self.fetch_weather_data)
        self.weather_update_timer.start(900000)  # 15 dakika

    def init_ui_screen(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header widget
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_widget.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #0f0f0f);
            padding: 30px 40px;
            border-bottom: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #333333, stop:0.5 #555555, stop:1 #333333);
        """)

        # Logo placeholder
        self.logo_label = QLabel("🏥")
        self.logo_label.setStyleSheet("""
            QLabel {
                font-size: 80px;
                color: #4CAF50;
                background-color: #333333;
                border-radius: 60px;
                padding: 20px;
                border: 2px solid #555555;
            }
        """)
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.logo_label)

        # Title container
        title_container = QVBoxLayout()
        
        self.title_label = QLabel("Nöbetçi Eczaneler")
        title_font = QFont("Inter", 48, QFont.DemiBold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #cccccc); 
            text-align: left; 
            padding-left: 30px;
            font-weight: 500;
        """)
        title_container.addWidget(self.title_label)

        self.subtitle_label = QLabel(f"{self.target_display_region}")
        subtitle_font = QFont("Inter", 26, QFont.Normal)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setStyleSheet("""
            color: #FFFFFF;
            padding-left: 30px;
            margin-top: 8px;
            font-weight: 400;
        """)
        title_container.addWidget(self.subtitle_label)
        title_container.setSpacing(5)

        header_layout.addLayout(title_container)
        header_layout.addStretch(1)

        # Hava durumu ve saat
        self.weather_time_layout = QVBoxLayout()
        self.weather_time_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.weather_icon_text_layout = QHBoxLayout()
        self.weather_icon_text_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.weather_icon_text_layout.setSpacing(15)

        # Hava durumu ikonu
        self.weather_icon_label = QLabel()
        self.weather_icon_label.setFixedSize(90, 90)
        self.weather_icon_label.setAlignment(Qt.AlignCenter)
        self.weather_icon_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #444444, stop:1 #333333); 
            border-radius: 45px;
            border: 2px solid #666666;
        """)

        self.weather_icon_text_layout.addWidget(self.weather_icon_label)

        # Hava durumu metni
        self.weather_text_label = QLabel("Yükleniyor...")
        weather_font = QFont("Inter", 24, QFont.Light)
        self.weather_text_label.setFont(weather_font)
        self.weather_text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.weather_text_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #ffffff, stop:1 #dddddd);
            font-weight: 300;
        """)
        self.weather_text_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.weather_icon_text_layout.addWidget(self.weather_text_label)

        self.weather_time_layout.addLayout(self.weather_icon_text_layout)

        # Son güncelleme
        self.last_updated_label = QLabel("Son Güncelleme: Yükleniyor...")
        time_font = QFont("Inter", 18, QFont.Light)
        self.last_updated_label.setFont(time_font)
        self.last_updated_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.last_updated_label.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #999999, stop:1 #777777);
            font-weight: 200;
        """)
        self.weather_time_layout.addWidget(self.last_updated_label)

        header_layout.addLayout(self.weather_time_layout)
        main_layout.addWidget(header_widget)

        # Scroll Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(30, 40, 30, 40)
        self.scroll_area.setWidget(self.scroll_content_widget)
        
        main_layout.addWidget(self.scroll_area)

        # Ana stil
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #000000);
            }}
            QScrollArea {{
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #000000);
            }}
            QScrollBar:vertical {{
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a1a, stop:1 #222222);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #444444, stop:0.5 #555555, stop:1 #444444);
                border-radius: 6px;
                min-height: 30px;
                border: 1px solid #666666;
            }}
        """)

    def update_time_label(self):
        """Saat güncelle"""
        self.last_updated_label.setText(f"Son Güncelleme: {time.strftime('%d.%m.%Y %H:%M:%S')}")

    def get_weather_info(self, temp):
        """Sıcaklığa göre renk"""
        if temp >= 30:
            return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF5733, stop:1 #FFC300)"
        elif 20 <= temp < 30:
            return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFBD33, stop:1 #DBFF33)"
        elif 10 <= temp < 20:
            return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #33FFBD, stop:1 #3399FF)"
        elif 0 <= temp < 10:
            return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3366FF, stop:1 #6633FF)"
        else:
            return "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6633FF, stop:1 #CC33FF)"

    def fetch_weather_data(self):
        """OpenWeatherMap'ten hava durumu al"""
        if not OPENWEATHER_API_KEY:
            self.weather_text_label.setText("API Key Eksik!")
            return

        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={OPENWEATHER_CITY}&"
            f"appid={OPENWEATHER_API_KEY}&"
            f"units={OPENWEATHER_UNITS}&"
            f"lang={OPENWEATHER_LANG}"
        )
        
        try:
            response = requests.get(weather_url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()

            if weather_data.get('cod') == 200:
                main_data = weather_data.get('main')
                weather_array = weather_data.get('weather')

                if main_data and weather_array and len(weather_array) > 0:
                    weather_desc = weather_array[0].get('description', 'Bilinmiyor')
                    temp = main_data.get('temp')

                    if temp is not None:
                        icon_color = self.get_weather_info(temp)
                        
                        self.weather_text_label.setText(f"{temp:.1f}°C\n{weather_desc.capitalize()}")
                        self.weather_icon_label.setStyleSheet(f"""
                            background: {icon_color}; 
                            border-radius: 45px;
                            border: 2px solid #666666;
                        """)
                        
                        print(f"✅ Hava durumu güncellendi: {OPENWEATHER_CITY} - {temp:.1f}°C")
                    else:
                        self.weather_text_label.setText("Sıcaklık bilgisi eksik!")
                else:
                    self.weather_text_label.setText("Hava durumu bilgisi eksik!")
            else:
                self.weather_text_label.setText(f"Veri alınamadı: {weather_data.get('message', 'Bilinmeyen hata')}")
        except Exception as e:
            self.weather_text_label.setText("Bağlantı Hatası!")
            print(f"❌ Hava durumu hatası: {e}")

    def load_data(self):
        """Eczane verilerini yükle"""
        print("📊 Veriler yükleniyor...")
        self.last_updated_label.setText("Son Güncelleme: Veri çekiliyor...")
        QApplication.processEvents()

        # Eski kartları temizle
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Veriyi çek
        self.all_pharmacies = fetch_and_process_data(target_bolge=self.target_display_region)

        if self.all_pharmacies:
            self.display_pharmacies()
            print(f"✅ Veri yüklendi. {len(self.all_pharmacies)} eczane bulundu.")
        else:
            print("❌ Veri yüklenemedi")
            error_label = QLabel("Nöbetçi eczane bilgileri yüklenemedi\n\nİnternet bağlantınızı kontrol edin")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("""
                color: #888888;
                padding: 80px;
                font-size: 32px;
                font-weight: 200;
            """)
            self.scroll_layout.addWidget(error_label)

    def display_pharmacies(self):
        """Eczaneleri görüntüle"""
        if not self.all_pharmacies:
            return

        for eczane in self.all_pharmacies:
            self.scroll_layout.addWidget(self.create_eczane_card(eczane))

    def create_eczane_card(self, eczane_info):
        """Eczane kartı oluştur"""
        card_widget = QWidget()
        card_layout = QVBoxLayout()
        card_widget.setLayout(card_layout)

        # Kart stili
        card_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252525, stop:1 #1e1e1e);
                border: 1px solid #444444;
                border-radius: 18px;
                padding: 0px; 
                margin: 0px; 
                margin-bottom: 35px;
            }}
            QLabel {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 21px;
                color: #f0f0f0;
                margin-bottom: 12px;
                background: transparent;
                font-weight: 300;
            }}
            QLabel.name {{
                font-size: 36px;
                font-weight: 600;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #e0e0e0);
                margin-bottom: 18px;
            }}
            QLabel.region {{
                font-size: 18px;  
                font-weight: 500;
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cccccc, stop:1 #aaaaaa); 
                margin-bottom: 8px;  
            }}
            QLabel.info {{
                font-size: 18px;  
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e8e8e8, stop:1 #d0d0d0);
                margin-bottom: 8px;  
                padding: 2px 0px;  
                font-weight: 300;
            }}
            QLabel#map_label {{ 
                background: #1a1a1a;
                border: 2px solid #444444;
                border-radius: 14px;
                padding: 0px; 
            }}
            QLabel#qr_label {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3a3a3a, stop:1 #303030);
                border: 2px solid #666666;
                border-radius: 14px;
                padding: 15px;
            }}
        """)

        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 10)
        card_widget.setGraphicsEffect(shadow)

        # Üst bölüm: Bilgi + QR
        top_section = QWidget()
        top_layout = QHBoxLayout(top_section)
        top_layout.setContentsMargins(35, 35, 35, 25)
        top_layout.setSpacing(40)  # Biraz daha fazla boşluk
        
        # Sol taraf - Bilgiler
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(15)  # Daha sade spacing
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Eczane adı
        name_label = QLabel(eczane_info['name'])
        name_label.setObjectName("name")
        name_font = QFont("Inter", 36, QFont.DemiBold)
        name_label.setFont(name_font)
        info_layout.addWidget(name_label)
        
        # Çizgiyi kaldırıyoruz - direkt bölge
        
        # Bölge
        region_label = QLabel(f"📍 {eczane_info['region']}")
        region_label.setObjectName("region")
        region_font = QFont("Inter", 18, QFont.Medium)  # Biraz küçülttük
        region_label.setFont(region_font)
        info_layout.addWidget(region_label)
        
        # Adres
        address_label = QLabel(f"🏠 {eczane_info['address']}")
        address_label.setObjectName("info")
        address_font = QFont("Inter", 18, QFont.Normal)  # Biraz küçülttük
        address_label.setFont(address_font)
        address_label.setWordWrap(True)
        info_layout.addWidget(address_label)
        
        # Telefon
        phone_label = QLabel(f"📞 {eczane_info['phone']}")
        phone_label.setObjectName("info")
        phone_font = QFont("Inter", 18, QFont.Normal)  # Biraz küçülttük
        phone_label.setFont(phone_font)
        info_layout.addWidget(phone_label)
        
        info_layout.addStretch()
        
        # Sağ taraf - QR kod bölümü
        qr_section = QVBoxLayout()
        qr_section.setAlignment(Qt.AlignCenter)
        qr_section.setSpacing(10)
        
        # QR başlık yazısı
        qr_title = QLabel("YOL TARİFİ İÇİN TARAYIN")
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Inter';
                margin-bottom: 5px;
            }
        """)
        qr_section.addWidget(qr_title)
        
        # QR kod
        qr_label = self.create_qr_code(eczane_info)
        qr_section.addWidget(qr_label)
        
        # QR widget container
        qr_container = QWidget()
        qr_container.setLayout(qr_section)
        
        top_layout.addWidget(info_widget, 1)
        top_layout.addWidget(qr_container, 0)
        card_layout.addWidget(top_section)

        # Alt bölüm: Harita
        map_widget = self.create_map_widget(eczane_info)
        if map_widget:
            card_layout.addWidget(map_widget)

        card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return card_widget

    def create_qr_code(self, eczane_info):
        """QR kod oluştur"""
        qr_label = QLabel()
        qr_label.setObjectName("qr_label")
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setFixedSize(140, 140)  # Biraz küçülttük

        if eczane_info['coordinates']['lat'] is not None and eczane_info['coordinates']['lon'] is not None:
            try:
                print(f"🔳 QR kod oluşturuluyor: {eczane_info['name']}")
                qr_map_url = (
                    f"https://www.google.com/maps/search/?api=1&query={eczane_info['coordinates']['lat']},{eczane_info['coordinates']['lon']}"
                )
                
                qr_img = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=6,  # Biraz küçülttük
                    border=2,
                )
                qr_img.add_data(qr_map_url)
                qr_img.make(fit=True)
                
                qr_pil_img = qr_img.make_image(fill_color="#e0e0e0", back_color="transparent")
                
                byte_array = BytesIO()
                qr_pil_img.save(byte_array, format="PNG")
                
                qr_pixmap = QPixmap()
                qr_pixmap.loadFromData(byte_array.getvalue())
                
                qr_label.setPixmap(qr_pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Küçülttük
                print(f"✅ QR kod oluşturuldu: {eczane_info['name']}")
                
            except Exception as e:
                print(f"❌ QR kod hatası: {e}")
                qr_label.setText("QR\nHata")
                qr_label.setStyleSheet("color: #FF6B6B; font-size: 12px; font-weight: 400;")
        else:
            qr_label.setText("QR\nYok")
            qr_label.setStyleSheet("color: #FF6B6B; font-size: 12px; font-weight: 400;")

        return qr_label

    def create_map_widget(self, eczane_info):
        """Harita widget'ı oluştur"""
        if (eczane_info['coordinates']['lat'] is None or 
            eczane_info['coordinates']['lon'] is None):
            print(f"⚠️ Koordinat yok, harita oluşturulmuyor: {eczane_info['name']}")
            return None

        try:
            print(f"🗺️ Harita oluşturuluyor: {eczane_info['name']}")
            
            # Rota polyline al
            route_polyline = get_driving_route_polyline(
                ECZANE_KUSDEMIR_LAT, ECZANE_KUSDEMIR_LON,
                eczane_info['coordinates']['lat'], eczane_info['coordinates']['lon'],
                GOOGLE_MAPS_API_KEY
            )

            map_container = QWidget()
            map_layout = QVBoxLayout(map_container)
            map_layout.setContentsMargins(25, 0, 25, 25)
            
            map_label = QLabel()
            map_label.setObjectName("map_label")
            map_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Google Static Maps API boyutları
            api_map_width = 900
            api_map_height = 700

            # Google Static Maps URL
            google_map_url_parts = [
                f"https://maps.googleapis.com/maps/api/staticmap?",
                f"size={api_map_width}x{api_map_height}&",
                f"scale=2&",
                # Karanlık tema stili
                f"style=feature:all|element:geometry|color:0x1a1a1a&",
                f"style=feature:all|element:labels.text.stroke|color:0x1a1a1a&",
                f"style=feature:all|element:labels.text.fill|color:0x888888&",
                f"style=feature:water|element:geometry|color:0x0f1419&",
                f"style=feature:road|element:geometry|color:0x2a2a2a&",
                f"style=feature:road|element:geometry.stroke|color:0x1a1a1a&",
                f"style=feature:administrative|element:geometry.stroke|color:0x444444&",
                f"style=feature:poi|element:labels.text.fill|color:0x666666&",
                f"markers=color:0x4CAF50%7Csize:mid%7Clabel:A%7C{ECZANE_KUSDEMIR_LAT},{ECZANE_KUSDEMIR_LON}&",
                f"markers=color:0xF44336%7Csize:mid%7Clabel:E%7C{eczane_info['coordinates']['lat']},{eczane_info['coordinates']['lon']}&"
            ]

            if route_polyline:
                google_map_url_parts.append(f"path=color:0x2196F3%7Cweight:6%7Cenc:{route_polyline}&")
                print(f"✅ Rota polyline eklendi")
            else:
                google_map_url_parts.append(f"center={eczane_info['coordinates']['lat']},{eczane_info['coordinates']['lon']}&zoom=14&")
                print(f"⚠️ Rota polyline yok, merkez koordinat kullanıldı")

            google_map_url_parts.append(f"key={GOOGLE_MAPS_API_KEY}")
            google_map_url = "".join(google_map_url_parts)
            
            print(f"🔗 Harita URL oluşturuldu: {len(google_map_url)} karakter")
            
            response = requests.get(google_map_url, stream=True, timeout=15)
            response.raise_for_status()

            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            if not pixmap.isNull():
                # Yuvarlatılmış köşeler
                rounded_pixmap = QPixmap(pixmap.size())
                rounded_pixmap.fill(Qt.transparent)
                
                painter = QPainter(rounded_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                path = QPainterPath()
                path.addRoundedRect(QRectF(rounded_pixmap.rect()), 14, 14)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                
                # Hedef boyutlar
                target_map_width_for_display = 810
                target_map_height_for_display = int(target_map_width_for_display * (api_map_height / api_map_width))

                map_label.setPixmap(rounded_pixmap.scaled(
                    QSize(target_map_width_for_display, target_map_height_for_display), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
                map_label.setAlignment(Qt.AlignCenter)
                map_layout.addWidget(map_label)
                
                print(f"✅ Harita oluşturuldu: {eczane_info['name']}")
                return map_container
            else:
                print(f"❌ Harita görüntüsü yüklenemedi: {eczane_info['name']}")
                return None
                
        except Exception as e:
            print(f"❌ Google Harita hatası: {e}")
            return None


# --- ANA UYGULAMA SINIFI ---
class EczaneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nöbetçi Eczaneler")
        self.setGeometry(100, 100, 900, 1600)
        
        # Tam ekran
        self.showFullScreen()

        # Ana layout
        self.main_app_layout = QVBoxLayout(self)
        self.main_app_layout.setContentsMargins(0, 0, 0, 0)
        self.main_app_layout.setSpacing(0)
        
        # Nöbetçi Eczane Ekranı
        self.nobetci_eczane_screen = NobetciEczaneScreen(self)
        self.main_app_layout.addWidget(self.nobetci_eczane_screen)

        # Ana stil
        self.setStyleSheet("""
            EczaneApp {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #050505, stop:1 #000000);
            }
        """)

    def keyPressEvent(self, event):
        """Klavye olayları"""
        # ESC ile tam ekrandan çık
        if event.key() == Qt.Key_Escape:
            self.showNormal()
        # F11 ile tam ekran toggle
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        # R ile manuel refresh
        elif event.key() == Qt.Key_R:
            print("🔄 Manuel veri yenileme")
            self.nobetci_eczane_screen.load_data()
        super().keyPressEvent(event)


if __name__ == "__main__":
    # Ana fonksiyon
    app = QApplication(sys.argv)
    
    # Modern font ayarları
    app.setStyleSheet("""
        * {
            font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            font-weight: 300;
            letter-spacing: 0.5px;
        }
    """)
    
    print("🚀 Nöbetçi Eczane Uygulaması Başlatılıyor...")
    print("📋 Kontroller:")
    print("   ESC: Tam ekrandan çık")
    print("   F11: Tam ekran toggle")
    print("   R: Manuel veri yenileme")
    
    # Uygulamayı başlat
    window = EczaneApp()
    window.show()
    
    sys.exit(app.exec_())
