def load_pharmacy_data_async(self):
        """Arka planda gerçek veriyi yükle"""
        try:
            print("Arka planda gerçek veriler yükleniyor...")
            # Buraya scraping kodu gelecek ama UI önce çalışsın
        except:
            print("Gerçek veri yüklenemedi, test verisi kullanılıyor")#!/usr/bin/env python3
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
    
    # API Keys
    GOOGLE_MAPS_API_KEY = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
    OPENWEATHER_API_KEY = "b0d1be7721b4967d8feb810424bd9b6f"
    
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
    
    # Spacing ve padding (DİKEY EKRAN KISALT)
    HEADER_HEIGHT = 120
    MAIN_PADDING = 20
    SECTION_SPACING = 25
    ELEMENT_SPACING = 15
    CARD_PADDING = 25

class SinglePharmacyWidget(QFrame):
    """Tek eczane widget'ı - tam ekran dikey layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # MANUEL TEST - gerçek KARŞIYAKA-4 adresi
        test_address = "SEMİKLER MAH. ANADOLU CAD. NO:591/B KARŞIYAKA İZMİR"
        real_coords = self.get_coordinates_from_address_test(test_address)
        
        self.pharmacy_data = {
            'name': 'TEST ECZANESİ (GEOCODING TEST)',
            'address': test_address,
            'phone': '02323301021',
            'district': 'KARŞIYAKA 4',
            'coordinates': real_coords
        }
        print(f"MANUEL TEST: {test_address} → {real_coords}")
        self.setup_ui()
    
    def get_coordinates_from_address_test(self, address):
        """MANUEL TEST - Geocoding çalışıyor mu?"""
        try:
            print(f"MANUEL GEOCODING TEST: {address}")
            
            geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': address,
                'key': Config.GOOGLE_MAPS_API_KEY,
                'region': 'tr',
                'language': 'tr'
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Geocoding response: {data}")
                
                if data['status'] == 'OK' and data['results']:
                    location = data['results'][0]['geometry']['location']
                    koordinatlar = [location['lat'], location['lng']]
                    print(f"BAŞARILI GEOCODING: {koordinatlar}")
                    return koordinatlar
                else:
                    print(f"Geocoding başarısız: {data}")
                    return [38.463, 27.115]
            else:
                print(f"HTTP hatası: {response.status_code}")
                return [38.463, 27.115]
                
        except Exception as e:
            print(f"Geocoding exception: {e}")
            return [38.463, 27.115]
    
    def load_pharmacy_data(self):
        """İzmir Eczacı Odası'ndan KARŞIYAKA-4 nöbetçi eczane verilerini çek - DÜZGÜN SCRAPİNG"""
        try:
            print("KARŞIYAKA-4 nöbetçi eczane bilgileri çekiliyor...")
            
            # İzmir Eczacı Odası form URL
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Bugünün tarihini al
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Form verisi - KARŞIYAKA 4 (value="770")
            form_data = {
                'tarih1': today,
                'ilce': '770'  # KARŞIYAKA 4
            }
            
            print(f"Form POST ediliyor: tarih={today}, ilce=770 (KARŞIYAKA 4)")
            
            # POST isteği gönder
            session = requests.Session()
            response = session.post(url, headers=headers, data=form_data, timeout=15)
            
            if response.status_code == 200:
                print("Form başarıyla gönderildi, HTML parse ediliyor...")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Eczane bilgilerini bul
                eczane_adi = None
                adres = None
                telefon = None
                
                # Telefon linklerini bul (tel: ile başlayanlar)
                tel_links = soup.find_all('a', href=lambda x: x and x.startswith('tel:'))
                
                for tel_link in tel_links:
                    telefon_raw = tel_link.get('href', '').replace('tel:', '').strip()
                    print(f"Telefon bulundu: {telefon_raw}")
                    
                    # Bu telefon numarasının etrafındaki elementleri kontrol et
                    parent_element = tel_link.parent
                    if parent_element:
                        # Aynı parent içinde eczane adı ve adres ara
                        parent_text = parent_element.get_text()
                        lines = parent_text.split('\n')
                        
                        for i, line in enumerate(lines):
                            line = line.strip()
                            
                            # Telefon satırını bul
                            if telefon_raw in line:
                                # Önceki satırlarda eczane adı ve adres ara
                                for j in range(max(0, i-10), i):
                                    prev_line = lines[j].strip()
                                    
                                    # Eczane adı (büyük harflerle ve ECZANESİ/ECZANE içeren)
                                    if ('ECZANESİ' in prev_line.upper() or 'ECZANE' in prev_line.upper()) and len(prev_line) > 5:
                                        if not eczane_adi or len(prev_line) > len(eczane_adi):
                                            eczane_adi = prev_line.strip()
                                            print(f"Eczane adı bulundu: {eczane_adi}")
                                    
                                    # Adres (MAH, MH, SOK, SK, CAD, NO içeren)
                                    elif any(keyword in prev_line.upper() for keyword in ['MAH.', 'MH.', 'SOK.', 'SK.', 'CAD.', 'NO:']):
                                        if not adres or len(prev_line) > len(adres):
                                            adres = prev_line.strip()
                                            print(f"Adres bulundu: {adres}")
                                
                                # Telefon numarasını temizle
                                telefon = re.sub(r'[^\d\s\-\(\)]', '', telefon_raw).strip()
                                break
                        
                        # Eğer bulduysak, döngüden çık
                        if eczane_adi and adres and telefon:
                            break
                
                # Eğer bulunamazsa, alternative parsing dene
                if not eczane_adi:
                    print("Alternative parsing deneniyor...")
                    
                    # Tüm div'leri kontrol et
                    all_divs = soup.find_all('div')
                    for div in all_divs:
                        div_text = div.get_text()
                        if 'KARŞIYAKA' in div_text.upper() and '4' in div_text:
                            lines = div_text.split('\n')
                            for line in lines:
                                line = line.strip()
                                if 'ECZANESİ' in line.upper() or 'ECZANE' in line.upper():
                                    eczane_adi = line
                                    print(f"Alternative parsing - Eczane adı: {eczane_adi}")
                                    break
                            break
                
                # Sonuçları değerlendir ve koordinat al
                if telefon:
                    final_eczane_adi = eczane_adi if eczane_adi else "KARŞIYAKA-4 NÖBETÇİ ECZANESİ"
                    final_adres = adres if adres else "Adres bilgisi parse edilemedi"
                    
                    # GERÇEK KOORDİNATLARI AL - Google Geocoding API
                    koordinatlar = self.get_coordinates_from_address(final_adres)
                    
                    self.pharmacy_data = {
                        'name': final_eczane_adi,
                        'address': final_adres,
                        'phone': telefon,
                        'district': 'KARŞIYAKA 4',
                        'coordinates': koordinatlar
                    }
                    print(f"BAŞARILI! Eczane bilgileri parse edildi:")
                    print(f"  Ad: {self.pharmacy_data['name']}")
                    print(f"  Adres: {self.pharmacy_data['address']}")
                    print(f"  Telefon: {self.pharmacy_data['phone']}")
                    print(f"  Koordinatlar: {koordinatlar}")
                    return
                else:
                    print("Hiçbir telefon numarası bulunamadı")
            else:
                print(f"Form POST hatası: HTTP {response.status_code}")
            
            # Hiçbir veri bulunamazsa varsayılan
            print("Veri parse edilemedi, varsayılan bilgiler kullanılıyor")
            self.pharmacy_data = {
                'name': 'VERİ PARSE EDİLEMEDİ',
                'address': 'İzmir Eczacı Odası sitesinden KARŞIYAKA-4 bilgisi alınamadı',
                'phone': 'Bilinmiyor',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]
            }
                
        except requests.RequestException as e:
            print(f"HTTP İsteği Hatası: {e}")
            self.pharmacy_data = {
                'name': 'BAĞLANTI HATASI',
                'address': 'İnternet bağlantısını kontrol edin',
                'phone': 'Bağlantı yok',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]
            }
        except Exception as e:
            print(f"Scraping Hatası: {e}")
            self.pharmacy_data = {
                'name': 'PARSE HATASI',
                'address': 'HTML parse edilemedi',
                'phone': 'Hata',
                'district': 'KARŞIYAKA 4',
                'coordinates': [38.463, 27.115]  # Varsayılan
            }
    
    def get_coordinates_from_address(self, address):
        """Adres bilgisinden Google Geocoding API ile koordinat al"""
        try:
            print(f"Koordinat alınıyor: {address}")
            
            # Adresi temizle
            clean_address = address + " İzmir Türkiye"
            
            # Google Geocoding API
            geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': clean_address,
                'key': Config.GOOGLE_MAPS_API_KEY,
                'region': 'tr',
                'language': 'tr'
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    location = data['results'][0]['geometry']['location']
                    koordinatlar = [location['lat'], location['lng']]
                    print(f"Koordinat bulundu: {koordinatlar}")
                    return koordinatlar
                else:
                    print(f"Geocoding hatası: {data.get('status', 'Bilinmeyen')}")
                    return [38.463, 27.115]  # Varsayılan Karşıyaka
            else:
                print(f"Geocoding HTTP hatası: {response.status_code}")
                return [38.463, 27.115]
                
        except Exception as e:
            print(f"Koordinat alma hatası: {e}")
            return [38.463, 27.115]  # Varsayılan koordinat
    
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
        
        # 6. Arka planda gerçek veriyi yükle
        QTimer.singleShot(2000, self.load_pharmacy_data_background)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def load_pharmacy_data_background(self):
        """Arka planda gerçek veriyi yükle ve UI'yi güncelle"""
        try:
            print("Arka planda gerçek KARŞIYAKA-4 verisi yükleniyor...")
            
            # GERÇEK SCRAPİNG - İzmir Eczacı Odası
            real_data = self.scrape_karsiyaka_4()
            
            if real_data:
                # Gerçek veri bulunduysa güncelle
                self.pharmacy_data = real_data
                print("UI güncelleniyor...")
                self.update_ui_data()
            else:
                print("Gerçek veri alınamadı, test verisi ile devam")
            
        except Exception as e:
            print(f"Arka plan veri yükleme hatası: {e}")
            print("Test verisi ile devam ediliyor")
    
    def scrape_karsiyaka_4(self):
        """KARŞIYAKA-4 eczanesini scraping ile al"""
        try:
            print("İzmir Eczacı Odası scraping başlıyor...")
            
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Form POST - KARŞIYAKA 4 (value="770")
            today = datetime.now().strftime("%Y-%m-%d")
            form_data = {'tarih1': today, 'ilce': '770'}
            
            response = requests.post(url, headers=headers, data=form_data, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Tel linklerini bul
                tel_links = soup.find_all('a', href=lambda x: x and x.startswith('tel:'))
                
                for tel_link in tel_links:
                    telefon = tel_link.get('href', '').replace('tel:', '').strip()
                    parent = tel_link.parent
                    
                    if parent:
                        parent_text = parent.get_text()
                        lines = [line.strip() for line in parent_text.split('\n') if line.strip()]
                        
                        eczane_adi = None
                        adres = None
                        
                        # Eczane adı ve adres ara
                        for line in lines:
                            # Eczane adı (ECZANESİ içeren)
                            if 'ECZANESİ' in line.upper() and len(line) > 5:
                                eczane_adi = line.strip()
                            
                            # Adres (MAH, SOK, NO içeren)
                            elif any(kw in line.upper() for kw in ['MAH.', 'SOK.', 'CAD.', 'NO:']):
                                adres = line.strip()
                        
                        # Eğer bulduysak koordinat al ve döndür
                        if telefon and (eczane_adi or adres):
                            if not eczane_adi:
                                eczane_adi = "KARŞIYAKA-4 NÖBETÇİ ECZANESİ"
                            if not adres:
                                adres = "Adres bilgisi bulunamadı"
                            
                            # Gerçek koordinatları al
                            koordinatlar = self.get_coordinates_from_address_test(adres + " İzmir")
                            
                            return {
                                'name': eczane_adi,
                                'address': adres,
                                'phone': telefon,
                                'district': 'KARŞIYAKA 4',
                                'coordinates': koordinatlar
                            }
            
            return None
            
        except Exception as e:
            print(f"Scraping hatası: {e}")
            return None
    
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
        name_label = QLabel(self.pharmacy_data.get('name', 'ECZANE İSMİ YÜKLENİYOR'))
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
        """UI'daki verileri güncelle - QR kod ve harita yenile"""
        try:
            print("UI verileri güncelleniyor...")
            
            # Tüm child widget'ları bul ve güncelle
            for widget in self.findChildren(QLabel):
                # Eczane adı güncelle
                if "TEST ECZANESİ" in widget.text():
                    widget.setText(self.pharmacy_data.get('name', 'ECZANE ADI YOK'))
                    print(f"Eczane adı güncellendi: {self.pharmacy_data.get('name')}")
                
                # Adres güncelle  
                elif "SEMİKLER MAH." in widget.text():
                    widget.setText(self.pharmacy_data.get('address', 'ADRES YOK'))
                    print(f"Adres güncellendi: {self.pharmacy_data.get('address')}")
                
                # Telefon güncelle
                elif widget.text().startswith('02323'):
                    widget.setText(self.pharmacy_data.get('phone', 'TELEFON YOK'))
                    print(f"Telefon güncellendi: {self.pharmacy_data.get('phone')}")
            
            # QR kod yenile
            self.refresh_qr_code()
            
            # Harita yenile
            self.refresh_map()
            
            print("UI güncelleme tamamlandı!")
            
        except Exception as e:
            print(f"UI güncelleme hatası: {e}")
    
    def refresh_qr_code(self):
        """QR kodu yenile"""
        try:
            print("QR kod yenileniyor...")
            new_qr = self.generate_qr_code()
            
            # QR widget'ını bul ve güncelle
            for widget in self.findChildren(QLabel):
                if widget.size() == QSize(300, 300):  # QR kod boyutu
                    if new_qr:
                        widget.setPixmap(new_qr)
                        widget.setStyleSheet("")  # Placeholder stilini kaldır
                        print("QR kod güncellendi")
                    break
                        
        except Exception as e:
            print(f"QR kod yenileme hatası: {e}")
    
    def refresh_map(self):
        """Haritayı yenile"""
        try:
            print("Harita yenileniyor...")
            # Harita yenileme kodunu buraya ekleyeceğiz
            print("Harita yenileme henüz implement edilmedi")
            
        except Exception as e:
            print(f"Harita yenileme hatası: {e}")
    
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
        """Harita ve yol tarifi bölümü - ROTA GÖSTERİMİ"""
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
        title_label = QLabel("🗺️ ROTA VE YOL TARİFİ")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.CONTENT_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 15px;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # ROTA HARİTASI - Google Maps ile GERÇEK YOL ROTASI
        map_widget = QLabel()
        map_widget.setFixedSize(1000, 400)
        
        # Koordinatlar
        start_lat, start_lon = 38.474356157028154, 27.112339648012767  # Senin konumun
        end_lat, end_lon = self.pharmacy_data['coordinates']  # Eczane konumu
        
        api_key = Config.GOOGLE_MAPS_API_KEY
        
        try:
            print(f"GERÇEK ROTA haritası yükleniyor...")
            print(f"Başlangıç: {start_lat},{start_lon}")
            print(f"Hedef: {end_lat},{end_lon}")
            
            # Önce Directions API ile gerçek rotayı al
            directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&key={api_key}"
            directions_response = requests.get(directions_url, timeout=10)
            
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                
                if directions_data['status'] == 'OK' and directions_data['routes']:
                    # Polyline'ı al (encoded route)
                    polyline = directions_data['routes'][0]['overview_polyline']['points']
                    
                    # Static Map API ile polyline'lı harita oluştur
                    maps_url = f"https://maps.googleapis.com/maps/api/staticmap?size=1000x400&path=enc:{polyline}&markers=color:green%7Clabel:S%7C{start_lat},{start_lon}&markers=color:red%7Clabel:E%7C{end_lat},{end_lon}&key={api_key}"
                    
                    map_response = requests.get(maps_url, timeout=15)
                    if map_response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        map_widget.setPixmap(pixmap.scaled(1000, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        print("GERÇEK ROTA haritası yüklendi!")
                    else:
                        print(f"Static Map API hatası: {map_response.status_code}")
                        self.set_map_placeholder(map_widget, "STATİC MAP HATASI")
                else:
                    print(f"Directions API hatası: {directions_data.get('status', 'Bilinmeyen hata')}")
                    self.set_map_placeholder(map_widget, "ROTA BULUNAMADI")
            else:
                print(f"Directions API HTTP hatası: {directions_response.status_code}")
                self.set_map_placeholder(map_widget, "DIRECTIONS API HATASI")
                
        except Exception as e:
            print(f"ROTA haritası hatası: {e}")
            self.set_map_placeholder(map_widget, "ROTA HATASI")
        
        # Harita'yı ortala
        map_container = QHBoxLayout()
        map_container.addStretch()
        map_container.addWidget(map_widget)
        map_container.addStretch()
        
        # ROTA BİLGİLERİ
        info_layout = QHBoxLayout()
        info_layout.setSpacing(50)
        
        # Sol: Hedef Adres
        address_layout = QVBoxLayout()
        addr_title = QLabel("🎯 HEDEF ECZANE")
        addr_title.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        
        addr_text = QLabel(f"📍 {self.pharmacy_data['address']}\n📞 {self.pharmacy_data['phone']}")
        addr_text.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                line-height: 1.4;
                background-color: rgba(0, 168, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid {Config.ACCENT_COLOR};
            }}
        """)
        addr_text.setWordWrap(True)
        
        address_layout.addWidget(addr_title)
        address_layout.addWidget(addr_text)
        
        # Sağ: Rota bilgisi
        distance_layout = QVBoxLayout()
        dist_title = QLabel("🚗 ROTA BİLGİSİ")
        dist_title.setStyleSheet(f"""
            QLabel {{
                color: {Config.SUCCESS_COLOR};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        
        # Basit mesafe hesaplama (yaklaşık)
        import math
        lat_diff = end_lat - start_lat
        lon_diff = end_lon - start_lon
        distance_km = math.sqrt(lat_diff**2 + lon_diff**2) * 111  # Yaklaşık km
        time_min = int(distance_km * 3)  # Yaklaşık dakika
        
        dist_text = QLabel(f"📍 Başlangıç: Mevcut konum\n🎯 Hedef: Nöbetçi eczane\n📏 Mesafe: ~{distance_km:.1f} km\n⏰ Süre: ~{time_min} dakika")
        dist_text.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                line-height: 1.4;
                background-color: rgba(46, 213, 115, 0.1);
                padding: 15px;
                border-radius: 10px;
                border: 1px solid {Config.SUCCESS_COLOR};
            }}
        """)
        
        distance_layout.addWidget(dist_title)
        distance_layout.addWidget(dist_text)
        
        info_layout.addLayout(address_layout)
        info_layout.addLayout(distance_layout)
        
        layout.addWidget(title_label)
        layout.addLayout(map_container)
        layout.addLayout(info_layout)
        section.setLayout(layout)
        return section
    
    def set_map_placeholder(self, map_widget, error_text="HARİTA YÜKLENEMEDİ"):
        """Harita placeholder'ı ayarla"""
        map_widget.setStyleSheet(f"""
            QLabel {{
                background-color: {Config.SECONDARY_BG};
                border: 3px solid {Config.ACCENT_COLOR};
                border-radius: 20px;
                color: {Config.PRIMARY_TEXT};
                font-size: {Config.SMALL_FONT_SIZE}px;
                font-weight: bold;
            }}
        """)
        map_widget.setText(f"🗺️ {error_text}\n\nGoogle Maps API\nkontrol edilsin")
        map_widget.setAlignment(Qt.AlignCenter)
    
    def create_qr_section(self):
        """QR kod bölümü - COMPACT"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.CARD_BG};
                border-radius: 15px;
                padding: 20px;
                border: 2px solid {Config.ACCENT_COLOR};
                max-height: 300px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(30)
        
        # QR kod - KÜÇÜK YAP
        qr_widget = QLabel()
        qr_widget.setFixedSize(250, 250)
        
        print("COMPACT QR kod oluşturuluyor...")
        qr_code = self.generate_qr_code()
        if qr_code:
            qr_widget.setPixmap(qr_code)
            qr_widget.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {Config.ACCENT_COLOR};
                    border-radius: 10px;
                    background-color: white;
                }}
            """)
            print("QR kod OK")
        else:
            print("QR kod HATA")
            qr_widget.setStyleSheet(f"""
                QLabel {{
                    background-color: red;
                    border: 2px solid white;
                    border-radius: 10px;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                }}
            """)
            qr_widget.setText("QR\nHATA")
            qr_widget.setAlignment(Qt.AlignCenter)
        
        # Açıklama - COMPACT
        info_layout = QVBoxLayout()
        
        title = QLabel("📱 TELEFON İLE OKUT")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)
        
        desc = QLabel("• Google Maps açılır\n• Senin konumundan\n• Eczaneye rota\n• Navigasyon başlar")
        desc.setStyleSheet(f"""
            QLabel {{
                color: {Config.PRIMARY_TEXT};
                font-size: 20px;
                line-height: 1.4;
                padding: 15px;
                background-color: rgba(0, 168, 255, 0.1);
                border-radius: 10px;
                border: 1px solid {Config.ACCENT_COLOR};
            }}
        """)
        
        info_layout.addWidget(title)
        info_layout.addWidget(desc)
        info_layout.addStretch()
        
        layout.addWidget(qr_widget)
        layout.addLayout(info_layout)
        layout.addStretch()
        
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
    """Hava durumu widget'ı - OpenWeatherMap API ile gerçek hava durumu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.weather_data = self.fetch_weather_data()
        self.setup_ui()
    
    def fetch_weather_data(self):
        """OpenWeatherMap API'sinden İzmir hava durumu çek"""
        try:
            api_key = Config.OPENWEATHER_API_KEY
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Izmir,TR&appid={api_key}&units=metric&lang=tr"
            
            print("Hava durumu verisi çekiliyor...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather = {
                    'temp': round(data['main']['temp']),
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['main']
                }
                print(f"Hava durumu: {weather['temp']}°C, {weather['description']}")
                return weather
            else:
                print(f"Hava durumu API hatası: {response.status_code}")
                return {'temp': 22, 'description': 'Bulutlu', 'icon': 'Clouds'}
                
        except Exception as e:
            print(f"Hava durumu hatası: {e}")
            return {'temp': 22, 'description': 'Veri yok', 'icon': 'Clear'}
    
    def get_weather_icon(self, icon_type):
        """Hava durumu ikonunu seç"""
        icons = {
            'Clear': '☀️',
            'Clouds': '☁️', 
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️'
        }
        return icons.get(icon_type, '🌤️')
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(Config.MAIN_PADDING, 15, Config.MAIN_PADDING, 15)
        layout.setSpacing(25)
        
        # Hava durumu ikonu ve sıcaklık
        weather_info = QHBoxLayout()
        weather_info.setSpacing(15)
        
        icon_label = QLabel(self.get_weather_icon(self.weather_data['icon']))
        icon_label.setStyleSheet(f"font-size: {Config.CONTENT_FONT_SIZE}px;")
        
        temp_label = QLabel(f"{self.weather_data['temp']}°C {self.weather_data['description']}")
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
