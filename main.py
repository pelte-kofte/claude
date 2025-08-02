#!/usr/bin/env python3
import sys
import os
import time
import logging
import json
import requests
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QScrollArea, QFrame, QGridLayout,
                             QStackedWidget, QSizePolicy)
from PyQt5.QtCore import (QTimer, QThread, pyqtSignal, Qt, QSize, QRect, 
                          QPropertyAnimation, QEasingCurve, pyqtSlot)
from PyQt5.QtGui import (QPixmap, QFont, QPainter, QPen, QBrush, QColor, 
                         QLinearGradient, QPalette, QIcon, QCursor)

# Local imports
from config import Config, Colors, Fonts, Styles, RaspberryPiConfig, is_raspberry_pi, is_test_environment

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

class DataFetcher(QThread):
    """Arka planda veri çekme sınıfı"""
    pharmacy_data_ready = pyqtSignal(list)
    weather_data_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def fetch_pharmacy_data(self):
        """İzmir Eczacı Odası'ndan nöbetçi eczane verilerini çeker"""
        try:
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # HTML parsing (basit regex ile)
            import re
            pharmacy_pattern = r'<div class="eczane-item.*?data-bolge="([^"]*)".*?<h3[^>]*>([^<]+)</h3>.*?<p[^>]*>([^<]+)</p>.*?<span[^>]*>([^<]+)</span>'
            
            pharmacies = []
            matches = re.findall(pharmacy_pattern, response.text, re.DOTALL)
            
            for match in matches:
                region, name, address, phone = match
                region = region.strip()
                
                if Config.TARGET_REGION.upper() in region.upper():
                    pharmacy = {
                        'name': name.strip(),
                        'address': address.strip(),
                        'phone': phone.strip(),
                        'region': region.strip(),
                        'coordinates': self.get_coordinates(address.strip())
                    }
                    pharmacies.append(pharmacy)
            
            self.pharmacy_data_ready.emit(pharmacies)
            logger.info(f"Fetched {len(pharmacies)} pharmacies for {Config.TARGET_REGION}")
            
        except Exception as e:
            logger.error(f"Error fetching pharmacy data: {e}")
            self.error_occurred.emit(f"Eczane verileri alınamadı: {str(e)}")
    
    def get_coordinates(self, address):
        """Adres için koordinat bilgilerini getirir (Nominatim)"""
        try:
            # Nominatim API (OpenStreetMap)
            query = f"{address}, {Config.CITY_NAME}, Turkey"
            url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
            
            headers = {'User-Agent': 'EczaneNobetSistemi/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'lat': float(data[0]['lat']),
                        'lon': float(data[0]['lon'])
                    }
            
            # Fallback: varsayılan koordinatlar
            return {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
            
        except Exception as e:
            logger.warning(f"Coordinate fetch failed for {address}: {e}")
            return {'lat': Config.DEFAULT_LAT, 'lon': Config.DEFAULT_LON}
    
    def fetch_weather_data(self):
        """OpenWeatherMap'ten hava durumu verilerini çeker"""
        try:
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
            
            self.weather_data_ready.emit(weather_info)
            logger.info(f"Weather data fetched: {weather_info['temperature']}°C")
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            self.error_occurred.emit(f"Hava durumu alınamadı: {str(e)}")
    
    def run(self):
        """Thread ana döngüsü"""
        self.fetch_pharmacy_data()
        self.fetch_weather_data()

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
        self.setFixedHeight(300)  # Dikey ekran için sabit yükseklik
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Eczane adı
        name_label = QLabel(self.pharmacy_data['name'])
        name_label.setStyleSheet(Styles.SUBTITLE_LABEL)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignTop)
        layout.addWidget(name_label)
        
        # Adres
        address_label = QLabel(self.pharmacy_data['address'])
        address_label.setStyleSheet(Styles.NORMAL_LABEL)
        address_label.setWordWrap(True)
        address_label.setAlignment(Qt.AlignTop)
        layout.addWidget(address_label)
        
        # Telefon
        phone_label = QLabel(f"📞 {self.pharmacy_data['phone']}")
        phone_label.setStyleSheet(Styles.NORMAL_LABEL)
        layout.addWidget(phone_label)
        
        # Alt kısım: QR ve Harita
        bottom_layout = QHBoxLayout()
        
        # QR Kod
        qr_widget = self.create_qr_widget()
        bottom_layout.addWidget(qr_widget)
        
        # Harita
        map_widget = self.create_map_widget()
        bottom_layout.addWidget(map_widget)
        
        layout.addLayout(bottom_layout)
        layout.addStretch()
    
    def create_qr_widget(self):
        """QR kod widget'ını oluşturur"""
        qr_widget = QWidget()
        qr_layout = QVBoxLayout(qr_widget)
        
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
        
        qr_text = QLabel("QR ile Yol Tarifi")
        qr_text.setStyleSheet(f"color: {Colors.SECONDARY_TEXT}; font-size: {Fonts.SMALL_SIZE}px;")
        qr_text.setAlignment(Qt.AlignCenter)
        
        qr_layout.addWidget(qr_label)
        qr_layout.addWidget(qr_text)
        
        return qr_widget
    
    def create_map_widget(self):
        """Harita widget'ını oluşturur"""
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        
        # Google Static Maps API
        coords = self.pharmacy_data['coordinates']
        map_url = (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={coords['lat']},{coords['lon']}&"
            f"zoom={Config.MAP_ZOOM}&"
            f"size={Config.MAP_WIDTH}x{Config.MAP_HEIGHT}&"
            f"markers=color:red%7C{coords['lat']},{coords['lon']}&"
            f"key={Config.GOOGLE_MAPS_API_KEY}"
        )
        
        # Harita resmini yükle
        try:
            response = requests.get(map_url, timeout=15)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                pixmap = pixmap.scaled(250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                map_label = QLabel()
                map_label.setPixmap(pixmap)
                map_label.setAlignment(Qt.AlignCenter)
                map_layout.addWidget(map_label)
            else:
                # Harita yüklenemedi
                error_label = QLabel("🗺️ Harita yüklenemedi")
                error_label.setStyleSheet(f"color: {Colors.WARNING_TEXT}; font-size: {Fonts.SMALL_SIZE}px;")
                error_label.setAlignment(Qt.AlignCenter)
                map_layout.addWidget(error_label)
                
        except Exception as e:
            logger.error(f"Map loading failed: {e}")
            error_label = QLabel("🗺️ Harita hatası")
            error_label.setStyleSheet(f"color: {Colors.ERROR_TEXT}; font-size: {Fonts.SMALL_SIZE}px;")
            error_label.setAlignment(Qt.AlignCenter)
            map_layout.addWidget(error_label)
        
        return map_widget

class HeaderWidget(QWidget):
    """Üst başlık widget'ı - dikey ekran için optimize"""
    
    def __init__(self):
        super().__init__()
        self.weather_data = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Header arayüzünü oluşturur"""
        self.setObjectName("header")
        self.setStyleSheet(Styles.HEADER)
        self.setFixedHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
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
        self.weather_label = QLabel()
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
    """Ana pencere sınıfı - Raspberry Pi dikey ekran için optimize"""
    
    def __init__(self):
        super().__init__()
        self.pharmacies = []
        self.setup_ui()
        self.setup_data_fetching()
        
    def setup_ui(self):
        """Ana arayüzü oluşturur"""
        self.setWindowTitle("Nöbetçi Eczane Sistemi")
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # Raspberry Pi modunda tam ekran ve imleç gizleme
        if Config.RASPBERRY_PI_MODE and is_raspberry_pi():
            if Config.FULLSCREEN:
                self.showFullScreen()
            if Config.HIDE_CURSOR:
                self.setCursor(QCursor(Qt.BlankCursor))
        else:
            # Test modunda pencere boyutu
            self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout (dikey)
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
        
        # Yükleme mesajı
        self.loading_label = QLabel("📡 Nöbetçi eczane bilgileri yükleniyor...")
        self.loading_label.setStyleSheet(Styles.TITLE_LABEL)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.loading_label)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Alt bilgi çubuğu
        footer = QLabel("💊 Karşıyaka 4. Bölge Nöbetçi Eczaneler • Otomatik güncelleme aktif")
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
    
    def setup_data_fetching(self):
        """Veri çekme timer'larını ayarlar"""
        # İlk veri çekme
        self.fetch_data()
        
        # Periyodik güncellemeler
        self.pharmacy_timer = QTimer()
        self.pharmacy_timer.timeout.connect(self.fetch_pharmacy_data)
        self.pharmacy_timer.start(Config.PHARMACY_UPDATE_INTERVAL)
        
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.fetch_weather_data)
        self.weather_timer.start(Config.WEATHER_UPDATE_INTERVAL)
    
    def fetch_data(self):
        """İlk veri yüklemesini başlatır"""
        self.fetch_pharmacy_data()
        self.fetch_weather_data()
    
    def fetch_pharmacy_data(self):
        """Eczane verilerini çeker"""
        self.data_fetcher = DataFetcher()
        self.data_fetcher.pharmacy_data_ready.connect(self.update_pharmacy_display)
        self.data_fetcher.error_occurred.connect(self.handle_error)
        self.data_fetcher.finished.connect(self.data_fetcher.deleteLater)
        self.data_fetcher.fetch_pharmacy_data()
    
    def fetch_weather_data(self):
        """Hava durumu verilerini çeker"""
        weather_fetcher = DataFetcher()
        weather_fetcher.weather_data_ready.connect(self.header.update_weather)
        weather_fetcher.error_occurred.connect(self.handle_error)
        weather_fetcher.finished.connect(weather_fetcher.deleteLater)
        weather_fetcher.fetch_weather_data()
    
    @pyqtSlot(list)
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
            
            # Tekrar deneme mesajı
            retry_label = QLabel("Sistem otomatik olarak güncelleme yapmaya devam edecek...")
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
                card = PharmacyCard(pharmacy)
                self.scroll_layout.addWidget(card)
        
        # Stretch ekle
        self.scroll_layout.addStretch()
        
        logger.info(f"UI updated with {len(pharmacies)} pharmacies")
    
    @pyqtSlot(str)
    def handle_error(self, error_message):
        """Hata mesajlarını işler"""
        logger.error(f"UI Error: {error_message}")
        
        # Hata gösterimi (eğer ekranda veri yoksa)
        if not self.pharmacies:
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
        """Klavye olayları (test için)"""
        if not Config.RASPBERRY_PI_MODE:
            if event.key() == Qt.Key_F11:
                # Tam ekran toggle
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.showFullScreen()
            elif event.key() == Qt.Key_R:
                # Manuel refresh
                self.fetch_data()
            elif event.key() == Qt.Key_Escape:
                # Çıkış (sadece test modunda)
                if not is_raspberry_pi():
                    self.close()
        
        super().keyPressEvent(event)

class RaspberryPiManager:
    """Raspberry Pi özel yönetici sınıfı"""
    
    def __init__(self):
        self.is_rpi = is_raspberry_pi()
        
    def setup_gpio(self):
        """GPIO pinlerini ayarlar (eğer gerekiyorsa)"""
        if not self.is_rpi:
            return
            
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(RaspberryPiConfig.STATUS_LED_PIN, GPIO.OUT)
            GPIO.output(RaspberryPiConfig.STATUS_LED_PIN, GPIO.HIGH)  # Durum LED'i yanar
            logger.info("GPIO setup completed")
        except ImportError:
            logger.warning("RPi.GPIO not available")
        except Exception as e:
            logger.error(f"GPIO setup failed: {e}")
    
    def cleanup_gpio(self):
        """GPIO temizliği"""
        if not self.is_rpi:
            return
            
        try:
            import RPi.GPIO as GPIO
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except:
            pass
    
    def check_system_resources(self):
        """Sistem kaynaklarını kontrol eder"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > RaspberryPiConfig.MAX_CPU_USAGE:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > RaspberryPiConfig.MAX_MEMORY_USAGE:
                logger.warning(f"High memory usage: {memory_percent}%")
                
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'status': 'healthy' if cpu_percent < RaspberryPiConfig.MAX_CPU_USAGE and memory_percent < RaspberryPiConfig.MAX_MEMORY_USAGE else 'warning'
            }
            
        except ImportError:
            logger.warning("psutil not available for resource monitoring")
            return {'status': 'unknown'}
        except Exception as e:
            logger.error(f"Resource check failed: {e}")
            return {'status': 'error'}

def setup_application():
    """Uygulama başlangıç ayarları"""
    app = QApplication(sys.argv)
    
    # Uygulama bilgileri
    app.setApplicationName("Nöbetçi Eczane Sistemi")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Claude Project")
    
    # Raspberry Pi özel ayarları
    if is_raspberry_pi():
        logger.info("Running on Raspberry Pi")
        # Ekran ayarları
        app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
        
        # Sistem bekletmesi engelleme (opsiyonel)
        try:
            os.system("xset s off")  # Screen saver off
            os.system("xset -dpms")  # Power management off
        except:
            pass
    else:
        logger.info("Running in test mode")
    
    return app

def main():
    """Ana fonksiyon"""
    logger.info("="*50)
    logger.info("Nöbetçi Eczane Sistemi Başlatılıyor...")
    logger.info(f"Raspberry Pi Mode: {Config.RASPBERRY_PI_MODE}")
    logger.info(f"Target Region: {Config.TARGET_REGION}")
    logger.info(f"Test Mode: {Config.TEST_MODE}")
    logger.info("="*50)
    
    # Raspberry Pi yöneticisini başlat
    rpi_manager = RaspberryPiManager()
    
    try:
        # GPIO setup
        rpi_manager.setup_gpio()
        
        # Başlatma gecikmesi (Raspberry Pi için)
        if is_raspberry_pi() and not Config.TEST_MODE:
            logger.info(f"Waiting {Config.AUTO_START_DELAY} seconds for system initialization...")
            time.sleep(Config.AUTO_START_DELAY)
        
        # Qt uygulamasını başlat
        app = setup_application()
        
        # Ana pencereyi oluştur
        window = MainWindow()
        window.show()
        
        # Sistem kaynak kontrolü (periyodik)
        if is_raspberry_pi():
            resource_timer = QTimer()
            resource_timer.timeout.connect(lambda: rpi_manager.check_system_resources())
            resource_timer.start(60000)  # Her dakika kontrol et
        
        logger.info("Application started successfully")
        
        # Event loop başlat
        exit_code = app.exec_()
        
        logger.info("Application shutting down...")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        return 1
    finally:
        # Temizlik
        rpi_manager.cleanup_gpio()
        logger.info("Cleanup completed")

if __name__ == "__main__":
    sys.exit(main())
