#!/usr/bin/env python3
import sys
import logging
import requests
from bs4 import BeautifulSoup
import qrcode
import json
import re
import time
from io import BytesIO
from datetime import datetime
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap

# Local imports
from config import Config, Colors, Fonts, Styles, is_raspberry_pi, is_test_environment

# Logging setup
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Thread'siz basit veri çekme sınıfı"""
    
    def __init__(self):
        pass
        
    def fetch_pharmacy_data(self):
        """İzmir Eczacı Odası'ndan gerçek nöbetçi eczane verilerini çeker - BeautifulSoup ile"""
        try:
            logger.info("Fetching real pharmacy data from İzmir Eczacı Odası...")
            
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
            }
            
            logger.info("Downloading pharmacy page...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # BeautifulSoup ile HTML parse et
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("Successfully parsed HTML with BeautifulSoup")
            
            pharmacies = []
            
            # Method 1: "KARŞIYAKA 4" kelimesini içeren tüm elementleri bul
            logger.info("Searching for KARŞIYAKA 4 elements...")
            
            # Tüm metinlerde "KARŞIYAKA 4" arama
            karşiyaka_elements = soup.find_all(text=re.compile(r'KARŞIYAKA\s*4', re.IGNORECASE))
            
            for element in karşiyaka_elements:
                logger.info(f"Found KARŞIYAKA 4 text: {element.strip()}")
                
                # Bu elementin parent'larından eczane bilgilerini bul
                parent = element.parent
                while parent and parent.name:
                    # Telefon linkini ara
                    phone_links = parent.find_all('a', href=re.compile(r'tel:'))
                    
                    if phone_links:
                        for phone_link in phone_links:
                            phone = phone_link.get('href').replace('tel:', '')
                            if len(phone) == 10:
                                phone = "0" + phone
                            
                            # Eczane adını bul - genelde yakınlardaki bold/strong text
                            pharmacy_name = "Bilinmeyen Eczane"
                            pharmacy_address = "Adres bulunamadı"
                            
                            # Parent'ın içindeki tüm text'leri kontrol et
                            all_texts = parent.get_text().split('\n')
                            for text in all_texts:
                                text = text.strip()
                                if text and len(text) > 5:
                                    # Eczane adı genelde "ECZANE" kelimesi içerir
                                    if 'ECZANE' in text.upper() and len(text) < 50:
                                        pharmacy_name = text.title()
                                    # Adres genelde MAH, CAD, SOK içerir
                                    elif any(word in text.upper() for word in ['MAH', 'CAD', 'SOK', 'BULV', 'CD']) and len(text) > 10:
                                        pharmacy_address = text
                            
                            pharmacy = {
                                'name': pharmacy_name,
                                'address': pharmacy_address,
                                'phone': phone,
                                'region': 'KARŞIYAKA 4',
                                'coordinates': self.get_coordinates(pharmacy_address)
                            }
                            pharmacies.append(pharmacy)
                            logger.info(f"Found pharmacy: {pharmacy_name} - {phone}")
                    
                    parent = parent.parent
                    if not parent:
                        break
            
            # Method 2: Telefon linklerinden geriye doğru KARŞIYAKA 4 ara
            if not pharmacies:
                logger.info("Method 1 failed, trying Method 2: scanning all phone links...")
                
                all_phone_links = soup.find_all('a', href=re.compile(r'tel:'))
                logger.info(f"Found {len(all_phone_links)} phone links total")
                
                for phone_link in all_phone_links:
                    phone = phone_link.get('href').replace('tel:', '')
                    if len(phone) == 10:
                        phone = "0" + phone
                    
                    # Bu telefon linkinin yakınındaki text'te KARŞIYAKA 4 var mı?
                    parent = phone_link.parent
                    context_text = ""
                    
                    # Yakındaki text'leri topla
                    for _ in range(5):  # 5 seviye yukarı git
                        if parent:
                            context_text += parent.get_text()
                            parent = parent.parent
                        else:
                            break
                    
                    # KARŞIYAKA 4 kontrolü
                    if re.search(r'KARŞIYAKA\s*4', context_text, re.IGNORECASE):
                        logger.info(f"Found KARŞIYAKA 4 context for phone: {phone}")
                        
                        # Eczane bilgilerini çıkar
                        lines = context_text.split('\n')
                        pharmacy_name = "Karşıyaka 4. Bölge Eczanesi"
                        pharmacy_address = "Adres bulunamadı"
                        
                        for line in lines:
                            line = line.strip()
                            if line and 'ECZANE' in line.upper() and len(line) < 50:
                                pharmacy_name = line.title()
                            elif any(word in line.upper() for word in ['MAH', 'CAD', 'SOK', 'BULV', 'CD']) and len(line) > 10 and len(line) < 100:
                                pharmacy_address = line
                        
                        pharmacy = {
                            'name': pharmacy_name,
                            'address': pharmacy_address,
                            'phone': phone,
                            'region': 'KARŞIYAKA 4',
                            'coordinates': self.get_coordinates(pharmacy_address)
                        }
                        pharmacies.append(pharmacy)
                        logger.info(f"Added pharmacy from Method 2: {pharmacy_name}")
            
            # Method 3: Sayfa içinde "24:00'DEN SONRA- KARŞIYAKA 4" pattern'ini ara
            if not pharmacies:
                logger.info("Method 2 failed, trying Method 3: searching for night duty pattern...")
                
                page_text = soup.get_text()
                karşiyaka_4_patterns = [
                    r'24:00.*?KARŞIYAKA\s*4.*?(\d{10,11})',
                    r'KARŞIYAKA\s*4.*?tel:(\d{10,11})',
                    r'SAAT.*?KARŞIYAKA\s*4.*?(\d{10,11})'
                ]
                
                for pattern in karşiyaka_4_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        phone = match
                        if len(phone) == 10:
                            phone = "0" + phone
                        
                        pharmacy = {
                            'name': 'Karşıyaka 4. Bölge Nöbetçi Eczanesi',
                            'address': 'Karşıyaka 4. Bölge, İzmir (Detay bilgi web sitesinde)',
                            'phone': phone,
                            'region': 'KARŞIYAKA 4',
                            'coordinates': {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
                        }
                        pharmacies.append(pharmacy)
                        logger.info(f"Found pharmacy with Method 3: {phone}")
            
            # Sonuç kontrolü
            if pharmacies:
                logger.info(f"SUCCESS: Found {len(pharmacies)} pharmacies for KARŞIYAKA 4")
                # Duplicate'leri temizle
                unique_pharmacies = []
                seen_phones = set()
                for pharmacy in pharmacies:
                    if pharmacy['phone'] not in seen_phones:
                        unique_pharmacies.append(pharmacy)
                        seen_phones.add(pharmacy['phone'])
                
                return unique_pharmacies
            else:
                logger.warning("No pharmacies found for KARŞIYAKA 4")
                
                # Sayfada KARŞIYAKA 4 var mı kontrol et
                page_text = soup.get_text()
                if re.search(r'KARŞIYAKA\s*4', page_text, re.IGNORECASE):
                    logger.info("KARŞIYAKA 4 exists on page but couldn't extract details")
                    return [{
                        'name': 'Karşıyaka 4. Bölge Nöbetçi Var',
                        'address': 'Karşıyaka 4. bölgesinde bugün nöbetçi eczane bulunuyor. Detay bilgiler için: https://www.izmireczaciodasi.org.tr/nobetci-eczaneler',
                        'phone': 'Web sitesinden kontrol edin',
                        'region': 'KARŞIYAKA 4',
                        'coordinates': {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
                    }]
                else:
                    logger.info("KARŞIYAKA 4 not found in today's duty list")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in web scraping with BeautifulSoup: {e}")
            return self.get_fallback_data()
    
    def get_fallback_data(self):
        """Gerçek veri alınamadığında fallback verisi"""
        logger.info("Using fallback data - real scraping failed")
        return [
            {
                'name': 'Veri Çekme Hatası',
                'address': f'{Config.TARGET_REGION} bölgesindeki nöbetçi eczane verileri şu anda çekilemiyor. İnternet bağlantınızı kontrol edin. Manuel kontrol: https://www.izmireczaciodasi.org.tr/nobetci-eczaneler',
                'phone': 'Web sitesinden kontrol edin',
                'region': Config.TARGET_REGION,
                'coordinates': {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
            }
        ]
    
    def get_coordinates(self, address):
        """Adres için koordinat bilgilerini getirir"""
        try:
            if not address or address == 'Adres bilgisi yok':
                return {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
            
            # Nominatim API (OpenStreetMap) - Rate limit için gecikme
            import time
            time.sleep(1)  # 1 saniye bekle
            
            query = f"{address}, {Config.CITY_NAME}, Turkey"
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'tr'
            }
            headers = {'User-Agent': 'EczaneNobetSistemi/1.0 (claude@anthropic.com)'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'lat': float(data[0]['lat']),
                        'lon': float(data[0]['lon'])
                    }
            
            # Fallback: Karşıyaka varsayılan koordinatları
            return {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
            
        except Exception as e:
            logger.warning(f"Coordinate fetch failed for {address}: {e}")
            return {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
    
    def fetch_weather_data(self):
        """Hava durumu verilerini çeker"""
        try:
            logger.info("Fetching weather data...")
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f'{Config.CITY_NAME},TR',
                'appid': Config.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'feels_like': round(data['main']['feels_like']),
                'icon': data['weather'][0]['icon']
            }
            
            logger.info(f"Weather fetched: {weather_info['temperature']}°C - {weather_info['description']}")
            return weather_info
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            # Test verisi döner
            return {
                'temperature': 22,
                'description': 'Test Modu',
                'humidity': 65,
                'feels_like': 24,
                'icon': '01d'
            }

class PharmacyCard(QFrame):
    """Tek eczane kartı widget'ı"""
    
    def __init__(self, pharmacy_data):
        super().__init__()
        self.pharmacy_data = pharmacy_data
        self.setup_ui()
        
    def setup_ui(self):
        """Kart arayüzünü oluşturur"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(Styles.CARD)
        self.setFixedHeight(280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Eczane adı
        name_label = QLabel(self.pharmacy_data['name'])
        name_label.setStyleSheet(Styles.SUBTITLE_LABEL)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Adres
        address_label = QLabel(self.pharmacy_data['address'])
        address_label.setStyleSheet(Styles.NORMAL_LABEL)
        address_label.setWordWrap(True)
        layout.addWidget(address_label)
        
        # Telefon
        phone_label = QLabel(f"📞 {self.pharmacy_data['phone']}")
        phone_label.setStyleSheet(Styles.NORMAL_LABEL)
        layout.addWidget(phone_label)
        
        # Alt kısım: QR kod
        qr_widget = self.create_qr_widget()
        layout.addWidget(qr_widget)
        
        layout.addStretch()
    
    def create_qr_widget(self):
        """QR kod widget'ını oluşturur"""
        qr_widget = QWidget()
        qr_layout = QHBoxLayout(qr_widget)
        qr_layout.setContentsMargins(0, 10, 0, 0)
        
        try:
            # QR kod oluştur
            coords = self.pharmacy_data['coordinates']
            maps_url = f"https://www.google.com/maps?q={coords['lat']},{coords['lon']}"
            
            qr = qrcode.QRCode(version=1, box_size=3, border=2)
            qr.add_data(maps_url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="white", back_color="black")
            
            # QPixmap'e dönüştür
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(Config.QR_SIZE, Config.QR_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            qr_label = QLabel()
            qr_label.setPixmap(pixmap)
            qr_label.setAlignment(Qt.AlignCenter)
            
            # QR açıklama
            qr_text_layout = QVBoxLayout()
            qr_text = QLabel("📱 QR Kod ile\nYol Tarifi")
            qr_text.setStyleSheet(f"color: {Colors.SECONDARY_TEXT}; font-size: {Fonts.SMALL_SIZE}px;")
            qr_text.setAlignment(Qt.AlignCenter)
            qr_text_layout.addWidget(qr_text)
            
            # Google Maps link
            coords_text = QLabel(f"📍 {coords['lat']:.4f}, {coords['lon']:.4f}")
            coords_text.setStyleSheet(f"color: {Colors.ACCENT_TEXT}; font-size: {Fonts.TINY_SIZE}px;")
            coords_text.setAlignment(Qt.AlignCenter)
            qr_text_layout.addWidget(coords_text)
            
            # Layout'a ekle
            qr_layout.addWidget(qr_label)
            qr_layout.addLayout(qr_text_layout)
            qr_layout.addStretch()
            
            logger.info(f"QR code generated for {self.pharmacy_data['name']}")
            
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            error_label = QLabel("❌ QR Kod Hatası")
            error_label.setStyleSheet(f"color: {Colors.ERROR_TEXT}; font-size: {Fonts.SMALL_SIZE}px;")
            error_label.setAlignment(Qt.AlignCenter)
            qr_layout.addWidget(error_label)
        
        return qr_widget

class HeaderWidget(QWidget):
    """Üst başlık widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.weather_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Header arayüzünü oluşturur"""
        self.setObjectName("header")
        self.setStyleSheet(Styles.HEADER)
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Sol taraf: Logo ve başlık
        left_layout = QVBoxLayout()
        
        title_label = QLabel("🏥 NÖBETÇİ ECZANELER")
        title_label.setStyleSheet(Styles.TITLE_LABEL)
        left_layout.addWidget(title_label)
        
        region_label = QLabel(f"📍 {Config.TARGET_REGION}")
        region_label.setStyleSheet(Styles.SUBTITLE_LABEL)
        left_layout.addWidget(region_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Sağ taraf: Tarih, saat, hava durumu
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # Tarih ve saat
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.PRIMARY_TEXT};
                font-size: {Fonts.TIME_SIZE}px;
                font-weight: bold;
                text-align: right;
            }}
        """)
        self.datetime_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.datetime_label)
        
        # Hava durumu
        self.weather_label = QLabel("🌡️ Yükleniyor...")
        self.weather_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.ACCENT_TEXT};
                font-size: {Fonts.SUBTITLE_SIZE}px;
                text-align: right;
            }}
        """)
        self.weather_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.weather_label)
        
        layout.addLayout(right_layout)
        
        # Zaman güncellemesi için timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_datetime)
        self.time_timer.start(Config.TIME_UPDATE_INTERVAL)
        self.update_datetime()
    
    def update_datetime(self):
        """Tarih ve saati günceller"""
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")
        day_str = now.strftime("%A")
        
        # Türkçe gün isimleri
        day_names = {
            'Monday': 'Pazartesi', 'Tuesday': 'Salı', 'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe', 'Friday': 'Cuma', 'Saturday': 'Cumartesi', 'Sunday': 'Pazar'
        }
        day_tr = day_names.get(day_str, day_str)
        
        datetime_text = f"{time_str}\n{date_str} {day_tr}"
        self.datetime_label.setText(datetime_text)
    
    def update_weather(self, weather_data):
        """Hava durumu bilgilerini günceller"""
        self.weather_data = weather_data
        
        temp = weather_data.get('temperature', 0)
        desc = weather_data.get('description', 'Bilinmiyor')
        
        # Sıcaklığa göre renk seçimi
        if temp < 10:
            temp_color = Colors.TEMP_COLD
        elif temp < 20:
            temp_color = Colors.TEMP_MILD
        elif temp < 30:
            temp_color = Colors.TEMP_WARM
        else:
            temp_color = Colors.TEMP_HOT
        
        weather_text = f"🌡️ {temp}°C\n{desc}"
        self.weather_label.setText(weather_text)
        self.weather_label.setStyleSheet(f"""
            QLabel {{
                color: {temp_color};
                font-size: {Fonts.SUBTITLE_SIZE}px;
                font-weight: 500;
                text-align: right;
            }}
        """)

class MainWindow(QMainWindow):
    """Ana pencere sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.pharmacies = []
        self.data_fetcher = DataFetcher()
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """Ana arayüzü oluşturur"""
        self.setWindowTitle("Nöbetçi Eczane Sistemi - Test Modu")
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)
        
        # İçerik alanı
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(Styles.SCROLLBAR)
        
        # Scroll widget
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # İlk yükleme mesajı
        loading_label = QLabel("📡 Veriler yükleniyor...")
        loading_label.setStyleSheet(Styles.TITLE_LABEL)
        loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(loading_label)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Alt bilgi çubuğu
        footer = QLabel("💊 Test Modu Aktif • F11: Tam Ekran • R: Yenile • ESC: Çıkış")
        footer.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.SECONDARY_BG};
                color: {Colors.SECONDARY_TEXT};
                font-size: {Fonts.SMALL_SIZE}px;
                padding: 8px;
                border-top: 1px solid {Colors.BORDER_COLOR};
                text-align: center;
            }}
        """)
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def setup_timers(self):
        """Timer'ları ayarlar"""
        # İlk veri yükleme (2 saniye sonra)
        QTimer.singleShot(2000, self.load_initial_data)
        
        # Hava durumu timer'ı (15 dakikada bir)
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.fetch_weather_data)
        self.weather_timer.start(Config.WEATHER_UPDATE_INTERVAL)
        
        # Eczane veri timer'ı (2 saatte bir)
        self.pharmacy_timer = QTimer()
        self.pharmacy_timer.timeout.connect(self.fetch_pharmacy_data)
        self.pharmacy_timer.start(Config.PHARMACY_UPDATE_INTERVAL)
    
    def load_initial_data(self):
        """İlk veri yüklemesini yapar"""
        logger.info("Loading initial data...")
        self.fetch_pharmacy_data()
        self.fetch_weather_data()
    
    def fetch_pharmacy_data(self):
        """Eczane verilerini çeker"""
        try:
            pharmacies = self.data_fetcher.fetch_pharmacy_data()
            self.update_pharmacy_display(pharmacies)
        except Exception as e:
            logger.error(f"Error fetching pharmacy data: {e}")
            self.show_error(f"Eczane verileri yüklenemedi: {str(e)}")
    
    def fetch_weather_data(self):
        """Hava durumu verilerini çeker"""
        try:
            weather_data = self.data_fetcher.fetch_weather_data()
            self.header.update_weather(weather_data)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
    
    def update_pharmacy_display(self, pharmacies):
        """Eczane listesini günceller"""
        self.pharmacies = pharmacies
        
        # Önceki widget'ları temizle
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not pharmacies:
            # Eczane bulunamadı
            no_pharmacy_label = QLabel("⚠️ Şu anda nöbetçi eczane bulunamadı")
            no_pharmacy_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.WARNING_TEXT};
                    font-size: {Fonts.TITLE_SIZE}px;
                    font-weight: bold;
                    padding: 40px;
                    text-align: center;
                }}
            """)
            no_pharmacy_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(no_pharmacy_label)
        else:
            # Başlık
            title_label = QLabel(f"🏥 {len(pharmacies)} Nöbetçi Eczane Bulundu")
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.ACCENT_TEXT};
                    font-size: {Fonts.TITLE_SIZE}px;
                    font-weight: bold;
                    padding: 20px 10px;
                    text-align: center;
                }}
            """)
            title_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(title_label)
            
            # Eczane kartları
            for pharmacy in pharmacies:
                try:
                    card = PharmacyCard(pharmacy)
                    self.scroll_layout.addWidget(card)
                except Exception as e:
                    logger.error(f"Error creating pharmacy card: {e}")
        
        # Stretch ekle
        self.scroll_layout.addStretch()
        
        logger.info(f"UI updated with {len(pharmacies)} pharmacies")
    
    def show_error(self, error_message):
        """Hata mesajını gösterir"""
        # Önceki widget'ları temizle
        for i in reversed(range(self.scroll_layout.count())):
            child = self.scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        error_label = QLabel(f"❌ {error_message}")
        error_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.ERROR_TEXT};
                font-size: {Fonts.SUBTITLE_SIZE}px;
                font-weight: bold;
                padding: 30px;
                text-align: center;
            }}
        """)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        self.scroll_layout.addWidget(error_label)
        
        retry_label = QLabel("🔄 Sistem otomatik olarak tekrar deneyecek...")
        retry_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.SECONDARY_TEXT};
                font-size: {Fonts.NORMAL_SIZE}px;
                padding: 20px;
                text-align: center;
            }}
        """)
        retry_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(retry_label)
    
    def keyPressEvent(self, event):
        """Klavye olayları"""
        if event.key() == Qt.Key_F11:
            # Tam ekran toggle
            if self.isFullScreen():
                self.showNormal()
                logger.info("Switched to windowed mode")
            else:
                self.showFullScreen()
                logger.info("Switched to fullscreen mode")
        elif event.key() == Qt.Key_R:
            # Manuel refresh
            logger.info("Manual refresh triggered")
            self.load_initial_data()
        elif event.key() == Qt.Key_Escape:
            # Çıkış
            logger.info("Exit triggered by user")
            self.close()
        
        super().keyPressEvent(event)

def main():
    """Ana fonksiyon"""
    logger.info("="*50)
    logger.info("Nöbetçi Eczane Sistemi Başlatılıyor - Thread'siz Mod")
    logger.info(f"Target Region: {Config.TARGET_REGION}")
    logger.info(f"Test Mode: {Config.TEST_MODE}")
    logger.info("="*50)
    
    try:
        # Qt uygulamasını başlat
        app = QApplication(sys.argv)
        app.setApplicationName("Nöbetçi Eczane Sistemi")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Claude Project")
        
        # Ana pencereyi oluştur
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        logger.info("Kontroller: F11=Tam Ekran, R=Yenile, ESC=Çıkış")
        
        # Event loop başlat
        exit_code = app.exec_()
        
        logger.info("Application shutting down...")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
