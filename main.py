#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Nöbetçi Eczane Gösterge Sistemi - TEK ECZANE DİKEY EKRAN
Karşıyaka-4 bölgesi için tek eczane gösterimi
"""

import sys
import requests
import bs4
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QScrollArea, QSizePolicy, QFrame, QGraphicsDropShadowEffect,
                             QStackedLayout, QMainWindow)
from PyQt5.QtGui import (QPixmap, QPainter, QPainterPath, QColor, QFont,
                          QLinearGradient, QRadialGradient, QBrush, QPen, QDesktopServices, QPalette)
from PyQt5.QtCore import Qt, QUrl, QTimer, QTime, QSize, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
import os
import re
import time
from io import BytesIO
from urllib.parse import quote_plus
from datetime import datetime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import qrcode
import base64

class Config:
    """Yapılandırma sınıfı"""
    # Ekran boyutları (dikey)
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 1920
    
    # Nöbet saatleri
    NOBET_START_TIME = QTime(18, 45)
    NOBET_END_TIME = QTime(8, 45)
    
    # API ayarları
    TARGET_REGION = "KARŞIYAKA 4"
    UPDATE_INTERVAL = 7200000  # 2 saat
    WEATHER_UPDATE_INTERVAL = 900000  # 15 dakika
    
    # Renkler
    PRIMARY_BG = "#0a0a0a"
    SECONDARY_BG = "#1a1a1a" 
    CARD_BG = "#1e1e1e"
    PRIMARY_TEXT = "#ffffff"
    SECONDARY_TEXT = "#b0b0b0"
    ACCENT_COLOR = "#00a8ff"
    SUCCESS_COLOR = "#2ed573"
    
    # Fontlar (dikey ekran için büyük)
    HEADER_FONT_SIZE = 42
    TITLE_FONT_SIZE = 36
    CONTENT_FONT_SIZE = 28
    SMALL_FONT_SIZE = 22
    
    # Spacing ve padding (dikey ekran optimize)
    HEADER_HEIGHT = 160
    MAIN_PADDING = 40
    SECTION_SPACING = 50
    ELEMENT_SPACING = 30
    CARD_PADDING = 40

class SinglePharmacyWidget(QFrame):
    """Tek eczane widget'ı - tam ekran dikey layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pharmacy_data = None
        self.load_pharmacy_data()
        self.setup_ui()
    
    def load_pharmacy_data(self):
        """İzmir Eczacı Odası'ndan KARŞIYAKA-4 nöbetçi eczane verilerini form POST ile çek"""
        try:
            # İzmir Eczacı Odası nöbetçi eczane sayfası
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://www.izmireczaciodasi.org.tr/nobetci-eczaneler'
            }
            
            print("KARŞIYAKA-4 için form POST ediliyor...")
            
            # Bugünün tarihini al
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Form verisi - KARŞIYAKA 4 seçimi (value="770")
            form_data = {
                'tarih1': today,
                'ilce': '770'  # KARŞIYAKA 4 için değer
            }
            
            # POST isteği gönder
            response = requests.post(url, headers=headers, data=form_data, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Eczane bilgilerini içeren div'leri bul
                # Genellikle adres, telefon gibi bilgiler div veya span içinde olur
                page_text = soup.get_text()
                lines = page_text.split('\n')
                
                eczane_adi = None
                adres = None
                telefon = None
                
                # Telefon ve adres pattern'ları ara
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # 0232 ile başlayan telefon numarası bul
                    if line.startswith('0232') or '[0232' in line:
                        telefon = re.sub(r'[^\d\s\-\(\)]', '', line)
                        telefon = telefon.strip()
                        
                        # Bu telefondan önce ve sonraki satırlarda adres ara
                        for j in range(max(0, i-5), min(len(lines), i+5)):
                            nearby_line = lines[j].strip()
                            
                            # Adres pattern'ı (MAH, MH, SOK, SK içeren)
                            if ('MAH.' in nearby_line or 'MH.' in nearby_line) and \
                               ('SOK.' in nearby_line or 'SK.' in nearby_line or 'BULV' in nearby_line or 'CAD' in nearby_line):
                                if not adres or len(nearby_line) > len(adres or ""):
                                    adres = nearby_line
                                    
                    # Eczane adı genellikle büyük harflerle yazılır ve "ECZANESİ" içerir
                    elif 'ECZANESİ' in line.upper() or 'ECZANE' in line.upper():
                        if len(line) > 3 and not line.startswith('0'):  # Telefon değilse
                            eczane_adi = line.upper()
                
                # Eğer veriler bulunduysa
                if telefon:
                    if not eczane_adi:
                        eczane_adi = "KARŞIYAKA-4 NÖBETÇİ ECZANESİ"
                    if not adres:
                        adres = "Adres bilgisi bulunamadı"
                    
                    self.pharmacy_data = {
                        'name': eczane_adi,
                        'address': adres,
                        'phone': telefon,
                        'district': 'KARŞIYAKA 4',
                        'coordinates': [38.463, 27.115]  # Karşıyaka merkez
                    }
                    print(f"KARŞIYAKA-4 eczane bulundu: {eczane_adi} - {telefon}")
                    return
                
                # Hiçbir veri bulunamadıysa
                print("POST sonrası veri bulunamadı, sayfa içeriği kontrol ediliyor...")
                
                # Sayfanın tamamını kontrol et
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    if 'tel:' in link['href']:
                        telefon_link = link['href'].replace('tel:', '').strip()
                        # Bu telefon numarasının etrafındaki elementleri kontrol et
                        parent = link.parent
                        if parent:
                            parent_text = parent.get_text(strip=True)
                            if parent_text:
                                # Basit parse
                                telefon = telefon_link
                                adres = "Adres: " + parent_text[:100] + "..."
                                eczane_adi = "KARŞIYAKA-4 NÖBETÇİ ECZANESİ"
                                
                                self.pharmacy_data = {
                                    'name': eczane_adi,
                                    'address': adres,
                                    'phone': telefon,
                                    'district': 'KARŞIYAKA 4',
                                    'coordinates': [38.463, 27.115]
                                }
                                print(f"Link'den KARŞIYAKA-4 bulundu: {telefon}")
                                return
            
            # Veri bulunamadıysa varsayılan
            print("Form POST ile veri alınamadı")
            self.pharmacy_data = {
                'name': 'KARŞIYAKA-4 VERİ YOK',
                'address': 'Form verisi alınamadı, lütfen manuel kontrol edin',
                'phone': 'Bilinmiyor',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]
            }
                
        except requests.RequestException as e:
            print(f"POST İsteği Hatası: {e}")
            self.pharmacy_data = {
                'name': 'BAĞLANTI HATASI',
                'address': 'İnternet bağlantısı kontrol edilsin',
                'phone': 'Bağlantı yok',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]
            }
        except Exception as e:
            print(f"Form POST Hatası: {e}")
            self.pharmacy_data = {
                'name': 'HATA OLUŞTU',
                'address': 'Form gönderimi başarısız',
                'phone': 'Hata',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]
            }
    
    def setup_ui(self):
        # Ana dikey layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Config.MAIN_PADDING, Config.MAIN_PADDING, 
                                     Config.MAIN_PADDING, Config.MAIN_PADDING)
        main_layout.setSpacing(Config.SECTION_SPACING)
        
        # 1. ECZANE ADI VE DURUM (Üst kısım)
        header_section = self.create_header_section()
        main_layout.addWidget(header_section)
        
        # 2. İLETİŞİM BİLGİLERİ (Orta-üst)
        contact_section = self.create_contact_section()
        main_layout.addWidget(contact_section)
        
        # 3. HARİTA VE YOL TARİFİ (Orta)
        map_section = self.create_map_section()
        main_layout.addWidget(map_section)
        
        # 4. QR KOD (Alt)
        qr_section = self.create_qr_section()
        main_layout.addWidget(qr_section)
        
        # 5. EK BİLGİLER (En alt)
        info_section = self.create_info_section()
        main_layout.addWidget(info_section)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def create_header_section(self):
        """Eczane adı ve durum bölümü"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 25px;
                padding: {Config.CARD_PADDING}px;
                border: 2px solid #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(Config.ELEMENT_SPACING)
        
        # Eczane adı
        name_label = QLabel(self.pharmacy_data['name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.TITLE_FONT_SIZE}px;
                font-weight: bold;
                text-align: center;
                padding: 20px 0px;
                letter-spacing: 2px;
            }}
        """)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        
        # Durum göstergesi
        status_container = QHBoxLayout()
        status_label = QLabel("● NÖBETÇİ")
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.SUCCESS_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                background-color: rgba(46, 213, 115, 0.15);
                padding: 15px 40px;
                border-radius: 20px;
                border: 2px solid {Config.SUCCESS_COLOR};
            }}
        """)
        status_label.setAlignment(Qt.AlignCenter)
        
        status_container.addStretch()
        status_container.addWidget(status_label)
        status_container.addStretch()
        
        layout.addWidget(name_label)
        layout.addLayout(status_container)
        section.setLayout(layout)
        return section
    
    def update_ui_data(self):
        """UI'daki verileri güncelle"""
        # Widget'ları yeniden oluştur
        self.setup_ui()
    
    def create_contact_section(self):
        """İletişim bilgileri bölümü"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 25px;
                padding: {Config.CARD_PADDING}px;
                border: 2px solid #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(Config.ELEMENT_SPACING)
        
        # Başlık
        title_label = QLabel("📋 İLETİŞİM BİLGİLERİ")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        
        # Adres
        address_container = QHBoxLayout()
        address_container.setSpacing(20)
        
        address_icon = QLabel("📍")
        address_icon.setStyleSheet(f"font-size: {Config.CONTENT_FONT_SIZE}px;")
        address_icon.setFixedWidth(50)
        
        address_text = QLabel(self.pharmacy_data['address'])
        address_text.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                line-height: 1.5;
                padding: 15px 0px;
            }}
        """)
        address_text.setWordWrap(True)
        
        address_container.addWidget(address_icon)
        address_container.addWidget(address_text, 1)
        
        # Telefon
        phone_container = QHBoxLayout()
        phone_container.setSpacing(20)
        
        phone_icon = QLabel("📞")
        phone_icon.setStyleSheet(f"font-size: {Config.CONTENT_FONT_SIZE}px;")
        phone_icon.setFixedWidth(50)
        
        phone_text = QLabel(self.pharmacy_data['phone'])
        phone_text.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: 500;
                padding: 15px 0px;
            }}
        """)
        
        phone_container.addWidget(phone_icon)
        phone_container.addWidget(phone_text, 1)
        
        layout.addWidget(title_label)
        layout.addLayout(address_container)
        layout.addLayout(phone_container)
        section.setLayout(layout)
        return section
    
    def create_map_section(self):
        """Harita ve yol tarifi bölümü"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 25px;
                padding: {Config.CARD_PADDING}px;
                border: 2px solid #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(Config.ELEMENT_SPACING)
        
        # Başlık
        title_label = QLabel("🗺️ HARİTA VE YOL TARİFİ")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Harita placeholder
        map_widget = QLabel()
        map_widget.setFixedSize(1000, 400)  # Dikey ekran için büyük harita
        map_widget.setStyleSheet(f"""
            QLabel {{
                background-color: {Config.SECONDARY_BG};
                border: 3px solid {Config.ACCENT_COLOR};
                border-radius: 20px;
            }}
        """)
        
        # Harita içeriği
        map_content = QVBoxLayout()
        map_content.setSpacing(20)
        
        map_title = QLabel("📍 ECZANE KONUMu")
        map_title.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
            }}
        """)
        map_title.setAlignment(Qt.AlignCenter)
        
        route_info = QLabel("🚗 Yaklaşık 5 dk mesafede\n📏 2.3 km uzaklık")
        route_info.setStyleSheet(f"""
            QLabel {{
                color: {Config.SECONDARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                text-align: center;
                line-height: 1.4;
            }}
        """)
        route_info.setAlignment(Qt.AlignCenter)
        
        map_content.addStretch()
        map_content.addWidget(map_title)
        map_content.addWidget(route_info)
        map_content.addStretch()
        
        map_widget.setLayout(map_content)
        
        # Harita'yı ortala
        map_container = QHBoxLayout()
        map_container.addStretch()
        map_container.addWidget(map_widget)
        map_container.addStretch()
        
        layout.addWidget(title_label)
        layout.addLayout(map_container)
        section.setLayout(layout)
        return section
    
    def create_qr_section(self):
        """QR kod bölümü"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 25px;
                padding: {Config.CARD_PADDING}px;
                border: 2px solid #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(Config.ELEMENT_SPACING)
        
        # Başlık
        title_label = QLabel("📱 QR KOD - YOL TARİFİ")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # QR kod container
        qr_container = QHBoxLayout()
        
        # QR kod
        qr_widget = QLabel()
        qr_widget.setFixedSize(300, 300)  # Dikey ekran için büyük QR
        
        qr_code = self.generate_qr_code()
        if qr_code:
            qr_widget.setPixmap(qr_code)
        else:
            qr_widget.setStyleSheet(f"""
                QLabel {{
                    background-color: white;
                    border: 3px solid {Config.ACCENT_COLOR};
                    border-radius: 20px;
                }}
            """)
            qr_widget.setText("QR KOD")
            qr_widget.setAlignment(Qt.AlignCenter)
        
        # QR açıklama
        qr_info = QVBoxLayout()
        qr_info.setSpacing(15)
        
        info_title = QLabel("Telefon ile okutun:")
        info_title.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
            }}
        """)
        
        info_desc = QLabel("• Google Maps'te aç\n• Yol tarifini al\n• Navigasyon başlat")
        info_desc.setStyleSheet(f"""
            QLabel {{
                color: {Config.SECONDARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                line-height: 1.6;
                padding: 10px;
                background-color: rgba(0, 168, 255, 0.1);
                border-radius: 15px;
                border: 1px solid {Config.ACCENT_COLOR};
            }}
        """)
        
        qr_info.addWidget(info_title)
        qr_info.addWidget(info_desc)
        qr_info.addStretch()
        
        qr_container.addStretch()
        qr_container.addWidget(qr_widget)
        qr_container.addSpacing(40)
        qr_container.addLayout(qr_info)
        qr_container.addStretch()
        
        layout.addWidget(title_label)
        layout.addLayout(qr_container)
        section.setLayout(layout)
        return section
    
    def create_info_section(self):
        """Ek bilgiler bölümü"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 25px;
                padding: {Config.CARD_PADDING}px;
                border: 2px solid #333333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Nöbet saatleri
        hours_label = QLabel("🕐 NÖBETÇİ SAATLERİ: 18:45 - 08:45")
        hours_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.SUCCESS_COLOR};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
                text-align: center;
                background-color: rgba(46, 213, 115, 0.1);
                padding: 20px;
                border-radius: 15px;
                border: 1px solid {Config.SUCCESS_COLOR};
            }}
        """)
        hours_label.setAlignment(Qt.AlignCenter)
        
        # Güncelleme bilgisi
        update_label = QLabel("📡 Son güncelleme: " + datetime.now().strftime("%d.%m.%Y %H:%M"))
        update_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.SECONDARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                text-align: center;
                padding: 10px;
            }}
        """)
        update_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(hours_label)
        layout.addWidget(update_label)
        section.setLayout(layout)
        return section
    
    def generate_qr_code(self):
        """QR kod oluştur - Google Maps linki"""
        try:
            # Google Maps URL oluştur
            lat, lon = self.pharmacy_data['coordinates']
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}&travelmode=driving"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=12,
                border=2,
            )
            qr.add_data(maps_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # QPixmap'e dönüştür
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.read())
            return pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except:
            return None

class WeatherWidget(QFrame):
    """Hava durumu widget'ı - header için"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(Config.MAIN_PADDING, 15, Config.MAIN_PADDING, 15)
        layout.setSpacing(25)
        
        # İkon ve sıcaklık
        weather_info = QHBoxLayout()
        weather_info.setSpacing(15)
        
        icon_label = QLabel("☀️")
        icon_label.setStyleSheet(f"font-size: {Config.CONTENT_FONT_SIZE}px;")
        
        temp_label = QLabel("24°C Açık")
        temp_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: 500;
            }}
        """)
        
        weather_info.addWidget(icon_label)
        weather_info.addWidget(temp_label)
        
        layout.addLayout(weather_info)
        layout.addStretch()
        
        # Tarih ve saat
        datetime_label = QLabel(f"{datetime.now().strftime('%d.%m.%Y %H:%M')}")
        datetime_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: 500;
            }}
        """)
        
        layout.addWidget(datetime_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    """Ana pencere - dikey ekran TEK ECZANE"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        # Pencere ayarları
        self.setWindowTitle("Nöbetçi Eczane - Karşıyaka 4")
        self.setFixedSize(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Config.PRIMARY_BG};
            }}
        """)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tek eczane widget'ı (scroll area içinde)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Config.PRIMARY_BG};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {Config.SECONDARY_BG};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Config.ACCENT_COLOR};
                border-radius: 4px;
                min-height: 20px;
            }}
        """)
        
        # Tek eczane widget'ı
        pharmacy_widget = SinglePharmacyWidget()
        scroll_area.setWidget(pharmacy_widget)
        
        main_layout.addWidget(scroll_area, 1)
        central_widget.setLayout(main_layout)
    
    def create_header(self):
        """Header oluştur"""
        header = QFrame()
        header.setFixedHeight(Config.HEADER_HEIGHT)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.SECONDARY_BG};
                border-bottom: 3px solid {Config.ACCENT_COLOR};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Başlık
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(Config.MAIN_PADDING, 20, Config.MAIN_PADDING, 0)
        
        title_label = QLabel("🏥 NÖBETÇİ ECZANE")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.HEADER_FONT_SIZE}px;
                font-weight: bold;
                letter-spacing: 3px;
            }}
        """)
        
        region_label = QLabel("KARŞIYAKA-4")
        region_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                background-color: rgba(0, 168, 255, 0.15);
                padding: 10px 20px;
                border-radius: 15px;
                border: 2px solid {Config.ACCENT_COLOR};
            }}
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(region_label)
        
        layout.addLayout(title_layout)
        
        # Hava durumu
        weather = WeatherWidget()
        layout.addWidget(weather)
        
        header.setLayout(layout)
        return header
    
    def setup_timers(self):
        """Timer'ları kur"""
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(60000)  # Her dakika
        
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(Config.UPDATE_INTERVAL)
    
    def update_clock(self):
        """Saati güncelle"""
        pass
    
    def update_data(self):
        """Karşıyaka-4 eczane verilerini güncelle"""
        print("Nöbetçi eczane verileri güncelleniyor...")
        # Ana widget'ın load_pharmacy_data metodunu çağır
        if hasattr(self.centralWidget().children()[0].widget(), 'load_pharmacy_data'):
            self.centralWidget().children()[0].widget().load_pharmacy_data()
            self.centralWidget().children()[0].widget().update_ui_data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Karanlık tema
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
