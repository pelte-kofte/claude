#!/usr/bin/env python3
import sys
import logging
import requests
from bs4 import BeautifulSoup
import qrcode
from io import BytesIO
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QScrollArea, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont

# Basit Config
class Config:
    GOOGLE_MAPS_API_KEY = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
    OPENWEATHER_API_KEY = "b0d1be7721b4967d8feb810424bd9b6f"
    TARGET_REGION = "KARŞIYAKA 4"
    CITY_NAME = "İzmir"
    WINDOW_WIDTH = 720
    WINDOW_HEIGHT = 1000
    DEFAULT_LAT = 38.4612
    DEFAULT_LON = 27.1285
    QR_SIZE = 120

# Renkler
class Colors:
    PRIMARY_BG = "#0a0a0a"
    SECONDARY_BG = "#1a1a1a"
    CARD_BG = "#1e1e1e"
    PRIMARY_TEXT = "#ffffff"
    SECONDARY_TEXT = "#cccccc"
    ACCENT_TEXT = "#4CAF50"
    WARNING_TEXT = "#FF9800"
    ERROR_TEXT = "#F44336"
    BORDER_COLOR = "#333333"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """Basit veri çekme"""
    
    def fetch_pharmacy_data(self):
        """KARŞIYAKA 4 eczanelerini çek"""
        try:
            logger.info("Fetching pharmacy data...")
            
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("HTML parsed successfully")
            
            # KARŞIYAKA 4 ara
            page_text = soup.get_text()
            if "KARŞIYAKA 4" not in page_text:
                logger.warning("KARŞIYAKA 4 not found")
                return []
            
            logger.info("KARŞIYAKA 4 found!")
            
            # Telefon linklerini bul
            phone_links = soup.find_all('a', href=lambda x: x and 'tel:' in x)
            
            for phone_link in phone_links:
                phone = phone_link.get('href').replace('tel:', '')
                if len(phone) == 10:
                    phone = "0" + phone
                
                # Parent text kontrol et
                parent = phone_link.parent
                context = ""
                for _ in range(2):
                    if parent:
                        context += parent.get_text()
                        parent = parent.parent
                
                # KARŞIYAKA 4 var mı?
                if "KARŞIYAKA 4" in context.upper():
                    logger.info(f"Found pharmacy: {phone}")
                    
                    # Basit parsing
                    lines = [line.strip() for line in context.split('\n') if line.strip()]
                    name = "Karşıyaka 4. Bölge Eczanesi"
                    address = "Karşıyaka, İzmir"
                    
                    for line in lines:
                        if 10 < len(line) < 100:
                            if any(word in line.upper() for word in ['MAH', 'CAD', 'SOK']):
                                address = line
                            elif 'ECZANE' in line.upper() and len(line) < 50:
                                name = line.title()
                    
                    return [{
                        'name': name,
                        'address': address,
                        'phone': phone,
                        'region': 'KARŞIYAKA 4'
                    }]
            
            # Telefon bulunamadı ama KARŞIYAKA 4 var
            return [{
                'name': 'Karşıyaka 4. Bölge Nöbetçi Eczanesi',
                'address': 'Bugün KARŞIYAKA 4 bölgesinde nöbetçi eczane var',
                'phone': 'Web sitesinden kontrol edin',
                'region': 'KARŞIYAKA 4'
            }]
                    
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def fetch_weather_data(self):
        """Hava durumu çek"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f'{Config.CITY_NAME},TR',
                'appid': Config.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            return {
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title()
            }
            
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return {'temperature': 25, 'description': 'Bilgi alınamadı'}

class PharmacyCard(QFrame):
    """Eczane kartı"""
    
    def __init__(self, pharmacy_data):
        super().__init__()
        self.pharmacy_data = pharmacy_data
        self.setup_ui()
        
    def setup_ui(self):
        """Kart UI"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.CARD_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        
        # Sol: Bilgiler
        info_layout = QVBoxLayout()
        
        # Eczane adı
        name_label = QLabel(self.pharmacy_data['name'])
        name_label.setFont(QFont('Arial', 18, QFont.Bold))
        name_label.setStyleSheet(f"color: {Colors.ACCENT_TEXT};")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # Adres
        address_label = QLabel(f"📍 {self.pharmacy_data['address']}")
        address_label.setFont(QFont('Arial', 12))
        address_label.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
        address_label.setWordWrap(True)
        info_layout.addWidget(address_label)
        
        # Telefon
        phone_label = QLabel(f"📞 {self.pharmacy_data['phone']}")
        phone_label.setFont(QFont('Arial', 14))
        phone_label.setStyleSheet(f"color: {Colors.PRIMARY_TEXT};")
        info_layout.addWidget(phone_label)
        
        # Bölge
        region_label = QLabel(f"🏢 {self.pharmacy_data['region']}")
        region_label.setFont(QFont('Arial', 12))
        region_label.setStyleSheet(f"color: {Colors.WARNING_TEXT};")
        info_layout.addWidget(region_label)
        
        layout.addLayout(info_layout, 2)
        
        # Sağ: QR kod
        qr_widget = self.create_qr_widget()
        layout.addWidget(qr_widget, 1)
    
    def create_qr_widget(self):
        """QR kod oluştur"""
        qr_container = QWidget()
        qr_layout = QVBoxLayout(qr_container)
        
        try:
            # Google Maps linki
            maps_url = f"https://www.google.com/maps?q={Config.DEFAULT_LAT},{Config.DEFAULT_LON}"
            
            # QR kod oluştur
            qr = qrcode.QRCode(version=1, box_size=3, border=2)
            qr.add_data(maps_url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="white", back_color="black")
            
            # QPixmap'e çevir
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            pixmap = pixmap.scaled(Config.QR_SIZE, Config.QR_SIZE, Qt.KeepAspectRatio)
            
            qr_label = QLabel()
            qr_label.setPixmap(pixmap)
            qr_label.setAlignment(Qt.AlignCenter)
            
            qr_text = QLabel("QR ile Yol Tarifi")
            qr_text.setFont(QFont('Arial', 10))
            qr_text.setStyleSheet(f"color: {Colors.SECONDARY_TEXT};")
            qr_text.setAlignment(Qt.AlignCenter)
            
            qr_layout.addWidget(qr_label)
            qr_layout.addWidget(qr_text)
            
        except Exception as e:
            logger.error(f"QR error: {e}")
            error_label = QLabel("QR Hatası")
            error_label.setStyleSheet(f"color: {Colors.ERROR_TEXT};")
            qr_layout.addWidget(error_label)
        
        return qr_container

class HeaderWidget(QWidget):
    """Üst başlık"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Header UI"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.SECONDARY_BG};
                border-bottom: 2px solid {Colors.ACCENT_TEXT};
                padding: 10px;
            }}
        """)
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        
        # Sol: Başlık
        left_layout = QVBoxLayout()
        
        title_label = QLabel("🏥 NÖBETÇİ ECZANELER")
        title_label.setFont(QFont('Arial', 20, QFont.Bold))
        title_label.setStyleSheet(f"color: {Colors.PRIMARY_TEXT};")
        left_layout.addWidget(title_label)
        
        region_label = QLabel(f"📍 {Config.TARGET_REGION}")
        region_label.setFont(QFont('Arial', 12))
        region_label.setStyleSheet(f"color: {Colors.ACCENT_TEXT};")
        left_layout.addWidget(region_label)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Sağ: Tarih ve hava
        right_layout = QVBoxLayout()
        
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.datetime_label.setStyleSheet(f"color: {Colors.PRIMARY_TEXT};")
        self.datetime_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.datetime_label)
        
        self.weather_label = QLabel("Yükleniyor...")
        self.weather_label.setFont(QFont('Arial', 12))
        self.weather_label.setStyleSheet(f"color: {Colors.ACCENT_TEXT};")
        self.weather_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(self.weather_label)
        
        layout.addLayout(right_layout)
        
        # Zaman timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()
    
    def update_datetime(self):
        """Tarih saat güncelle"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%H:%M:%S\n%d.%m.%Y"))
    
    def update_weather(self, weather_data):
        """Hava durumu güncelle"""
        temp = weather_data.get('temperature', 0)
        desc = weather_data.get('description', '')
        self.weather_label.setText(f"🌡️ {temp}°C\n{desc}")

class MainWindow(QMainWindow):
    """Ana pencere"""
    
    def __init__(self):
        super().__init__()
        self.data_fetcher = DataFetcher()
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """Ana UI"""
        self.setWindowTitle("Nöbetçi Eczane Sistemi")
        self.setStyleSheet(f"background-color: {Colors.PRIMARY_BG}; color: {Colors.PRIMARY_TEXT};")
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.header = HeaderWidget()
        layout.addWidget(self.header)
        
        # İçerik
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Yükleme mesajı
        self.loading_label = QLabel("📡 Yükleniyor...")
        self.loading_label.setFont(QFont('Arial', 16))
        self.loading_label.setStyleSheet(f"color: {Colors.ACCENT_TEXT}; padding: 20px;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.loading_label)
        
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        
        # Footer
        footer = QLabel("💊 F11: Tam Ekran • R: Yenile • ESC: Çıkış")
        footer.setFont(QFont('Arial', 10))
        footer.setStyleSheet(f"background-color: {Colors.SECONDARY_BG}; color: {Colors.SECONDARY_TEXT}; padding: 5px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
    
    def setup_timers(self):
        """Timer'lar"""
        QTimer.singleShot(1000, self.load_data)
        
        # Hava durumu timer
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.fetch_weather)
        self.weather_timer.start(15 * 60 * 1000)  # 15 dakika
        
        # Eczane timer
        self.pharmacy_timer = QTimer()
        self.pharmacy_timer.timeout.connect(self.fetch_pharmacies)
        self.pharmacy_timer.start(2 * 60 * 60 * 1000)  # 2 saat
    
    def load_data(self):
        """Veri yükle"""
        self.fetch_pharmacies()
        self.fetch_weather()
    
    def fetch_pharmacies(self):
        """Eczane verisi çek"""
        try:
            pharmacies = self.data_fetcher.fetch_pharmacy_data()
            self.update_pharmacy_display(pharmacies)
        except Exception as e:
            logger.error(f"Pharmacy fetch error: {e}")
            self.show_error("Eczane verileri yüklenemedi")
    
    def fetch_weather(self):
        """Hava durumu çek"""
        try:
            weather_data = self.data_fetcher.fetch_weather_data()
            self.header.update_weather(weather_data)
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
    
    def update_pharmacy_display(self, pharmacies):
        """Eczane listesi güncelle"""
        self.clear_layout()
        
        if not pharmacies:
            no_data_label = QLabel("⚠️ Bugün Karşıyaka 4. bölgede nöbetçi eczane bulunamadı")
            no_data_label.setFont(QFont('Arial', 16, QFont.Bold))
            no_data_label.setStyleSheet(f"color: {Colors.WARNING_TEXT}; padding: 30px;")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setWordWrap(True)
            self.scroll_layout.addWidget(no_data_label)
        else:
            # Başlık
            title_label = QLabel(f"🏥 {len(pharmacies)} Nöbetçi Eczane Bulundu")
            title_label.setFont(QFont('Arial', 18, QFont.Bold))
            title_label.setStyleSheet(f"color: {Colors.ACCENT_TEXT}; padding: 15px;")
            title_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(title_label)
            
            # Eczane kartları
            for pharmacy in pharmacies:
                card = PharmacyCard(pharmacy)
                self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()
        logger.info(f"UI updated with {len(pharmacies)} pharmacies")
    
    def clear_layout(self):
        """Layout temizle"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_error(self, error_message):
        """Hata göster"""
        self.clear_layout()
        
        error_label = QLabel(f"❌ {error_message}")
        error_label.setFont(QFont('Arial', 14, QFont.Bold))
        error_label.setStyleSheet(f"color: {Colors.ERROR_TEXT}; padding: 30px;")
        error_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(error_label)
    
    def keyPressEvent(self, event):
        """Klavye"""
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_R:
            logger.info("Manuel yenileme")
            self.load_data()
        elif event.key() == Qt.Key_Escape:
            self.close()

def main():
    """Ana fonksiyon"""
    logger.info("Nöbetçi Eczane Sistemi başlatılıyor...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Nöbetçi Eczane Sistemi")
    
    window = MainWindow()
    window.show()
    
    logger.info("Uygulama başlatıldı")
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
