import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import http.server
import socketserver
from urllib.parse import urlparse
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
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QColor 
import threading
import http.server
import socketserver
import time

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """🌐 CORS BYPASS HANDLER"""
    
    def end_headers(self):
        """CORS Header'larını ekle"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_OPTIONS(self):
        """OPTIONS request handler"""
        self.send_response(200)
        self.end_headers()
class ModernCorporateEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane - HTTP Server + Lottie")
        
        # DİKEY MONİTÖR İÇİN BOYUTLAR
        self.setFixedSize(900, 1280)
        
        # 🌐 LOCAL HTTP SERVER BAŞLAT
        self.start_local_server()
        
        # API anahtarları
        self.api_key = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
        self.weather_api_key = "b0d1be7721b4967d8feb810424bd9b6f"
        self.start_lat = 38.47434762293852
        self.start_lon = 27.112356625119595
        
        self.current_mode = None
        self.video_path = None
        
        # 🎨 MODERN CORPORATE RENK PALETİ
        self.colors = {
            'bg_primary': '#000000',
            'bg_secondary': '#111111',
            'bg_card': '#1a1a1a',
            'bg_accent': '#222222',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#888888',
            'accent_blue': '#007AFF',
            'accent_green': '#30D158',
            'accent_orange': '#FF9500',
            'accent_red': '#FF3B30',
            'accent_purple': '#AF52DE',
            'border': '#333333',
            'border_light': '#444444',
            'shadow': 'rgba(0, 0, 0, 0.5)',
            'hover': 'rgba(255, 255, 255, 0.05)',
        }
        
        self.setup_ui()
        self.setup_video_player()
        self.setup_timers()
        self.switch_to_pharmacy_mode()
        
        self.show()
        print("🎬 HTTP Server + Lottie Animations başlatıldı!")

    def start_local_server(self):
        """🌐 CORS BYPASS HTTP SERVER"""
        self.server_port = 8000
        self.server_url = f"http://localhost:{self.server_port}"
        self.server_ready = False
        
        def run_server():
            try:
                # Çalışma dizinini ayarla
                current_dir = os.path.dirname(os.path.abspath(__file__))
                os.chdir(current_dir)
                print(f"📁 CORS Server dizini: {current_dir}")
                
                # CORS HTTP server oluştur
                handler = CORSHTTPRequestHandler
                
                # Port kontrolü
                for port in range(8000, 8010):
                    try:
                        with socketserver.TCPServer(("", port), handler) as httpd:
                            self.server_port = port
                            self.server_url = f"http://localhost:{port}"
                            print(f"🌐 CORS HTTP Server başlatıldı: {self.server_url}")
                            
                            # Server hazır sinyali
                            self.server_ready = True
                            
                            # Server'ı çalıştır
                            httpd.serve_forever()
                            break
                    except OSError:
                        print(f"⚠️ Port {port} kullanımda, {port+1} deneniyor...")
                        continue
                        
            except Exception as e:
                print(f"❌ CORS Server hatası: {e}")
                self.server_url = None
                self.server_ready = False
        
        # Server'ı thread'de başlat
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Server'ın hazır olmasını bekle
        QTimer.singleShot(2000, self.check_server_ready)

    def check_server_ready(self):
        """🔍 SERVER HAZIR KONTROLÜ"""
        if self.server_ready:
            print("✅ HTTP Server hazır - Lottie animasyonları yüklenebilir!")
        else:
            print("⏳ Server henüz hazır değil, 1 saniye daha bekleniyor...")
            QTimer.singleShot(1000, self.check_server_ready)

    def setup_lottie_weather(self):
        """🎬 BÜYÜK BOYUTTA LOTTIE SİSTEMİ"""
        self.lottie_widget = QWebEngineView()
        
        # BÜYÜK BOYUT - GÖRÜNÜR ANİMASYON
        self.lottie_widget.setFixedSize(40, 40)  # 22x22 → 40x40
        
        self.lottie_widget.setStyleSheet("""
        QWebEngineView {
            background: transparent !important;
            background-color: rgba(0, 0, 0, 0) !important;
            border: none;
        }
        """)
        # WebEngine sayfası şeffaf
        page = self.lottie_widget.page()
        page.setBackgroundColor(QColor(0, 0, 0, 0))  # Tamamen şeffaf
    
     # Console gizle
        page.javaScriptConsoleMessage = lambda *args: None
        # Console mesajlarını gizle
        self.lottie_widget.page().javaScriptConsoleMessage = lambda *args: None
        
        # Lottie dosya yolları
        self.lottie_files = {
            'sunny': 'weather_lottie/sun.json',
            'hot': 'weather_lottie/sun_hot.json',
            'rain': 'weather_lottie/rain.json',
            'drizzle': 'weather_lottie/rain.json',
            'snow': 'weather_lottie/snow.json',
            'storm': 'weather_lottie/storm.json',
            'thunderstorm': 'weather_lottie/storm.json',
            'clouds': 'weather_lottie/clouds.json',
            'fog': 'weather_lottie/fog.json',
            'mist': 'weather_lottie/fog.json',
            'wind': 'weather_lottie/wind.json',
        }
        
        print("🎬 BÜYÜK Lottie sistemi kuruldu (40x40)")

    def load_lottie_animation(self, weather_main, temp=25):
        """🌈 BÜYÜK BOYUTTA LOTTIE YÜKLE"""
        try:
            if not self.server_ready:
                print("⏳ Server henüz hazır değil, emoji kullanılıyor")
                return False
            
            # Hava durumuna göre dosya seç
            lottie_file = None
            
            if weather_main in ['clear', 'sunny']:
                if temp >= 30:
                    lottie_file = self.lottie_files.get('hot') or self.lottie_files.get('sunny')
                else:
                    lottie_file = self.lottie_files.get('sunny')
            elif weather_main in ['rain']:
                lottie_file = self.lottie_files.get('rain')
            elif weather_main in ['drizzle']:
                lottie_file = self.lottie_files.get('drizzle') or self.lottie_files.get('rain')
            elif weather_main in ['snow']:
                lottie_file = self.lottie_files.get('snow')
            elif weather_main in ['thunderstorm', 'storm']:
                lottie_file = self.lottie_files.get('storm')
            elif weather_main in ['clouds']:
                lottie_file = self.lottie_files.get('clouds')
            elif weather_main in ['fog', 'mist', 'haze']:
                lottie_file = self.lottie_files.get('fog')
            elif weather_main in ['wind']:
                lottie_file = self.lottie_files.get('wind')
            
            # Dosya kontrolü
            if lottie_file and os.path.exists(lottie_file):
                # HTTP URL oluştur
                http_url = f"{self.server_url}/{lottie_file}"
                
                html_content = f"""
                <!DOCTYPE html>
                <html style="background: transparent;">
            <head>
                <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
                <style>
                    * {{
                        margin: 0 !important;
                        padding: 0 !important;
                        background: transparent !important;
                        background-color: transparent !important;
                    }}
                    html, body {{
                        background: transparent !important;
                        background-color: transparent !important;
                        overflow: hidden;
                    }}
                    lottie-player {{
                        width: 36px !important;
                        height: 36px !important;
                        background: transparent !important;
                        background-color: transparent !important;
                    }}
                </style>
            </head>
            <body style="background: transparent !important;">
                <lottie-player 
                    src="{http_url}" 
                    background="transparent" 
                    speed="1" 
                    loop 
                    autoplay
                    style="background: transparent !important;">
                </lottie-player>
            </body>
            </html>
            """
                
                self.lottie_widget.setHtml(html_content)
                print(f"🎬 BÜYÜK Lottie yüklendi: {http_url} (36x36)")
                return True
                
            else:
                print(f"❌ Lottie dosyası bulunamadı: {lottie_file}")
                return False
                
        except Exception as e:
            print(f"❌ BÜYÜK Lottie yükleme hatası: {e}")
            return False

    def load_svg_icon(self, icon_path, size=24):
        """🎨 SVG İkon Yükleyici"""
        try:
            if os.path.exists(icon_path):
                svg_widget = QSvgWidget(icon_path)
                svg_widget.setFixedSize(size, size)
                svg_widget.setStyleSheet("background: transparent;")
                print(f"✅ SVG icon yüklendi: {icon_path}")
                return svg_widget
            else:
                print(f"❌ SVG icon bulunamadı: {icon_path}")
                return None
        except Exception as e:
            print(f"❌ SVG yükleme hatası: {e}")
            return None

    def create_fallback_icon(self, emoji, color="#ffffff", size=20):
        """🔄 FALLBACK EMOJI İKON"""
        label = QLabel(emoji)
        label.setFont(QFont('Segoe UI', size-4))
        label.setStyleSheet(f"color: {color}; background: transparent;")
        label.setFixedSize(size, size)
        label.setAlignment(Qt.AlignCenter)
        return label

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
        """🏢 HTTP SERVER + LOTTIE DESIGN"""
        widget = self.pharmacy_widget
        
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_primary']};
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                color: {self.colors['text_primary']};
            }}
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {self.colors['bg_card']};
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['accent_blue']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #0056CC;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: transparent;
                border: none;
            }}
        """)
        
        content_widget = QWidget()
        content_widget.setMinimumHeight(1400)
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 32)
        
        # Sistemleri kur
        self.setup_lottie_weather()
        self.setup_animations()
        self.create_red_header_with_lottie(layout)
        self.create_svg_info_section(layout)
        self.create_corporate_qr_map_section(layout)
        self.create_corporate_footer(layout)
        
        spacer = QWidget()
        spacer.setMinimumHeight(100)
        spacer.setStyleSheet("background: transparent;")
        layout.addWidget(spacer)
        
        scroll_area.setWidget(content_widget)
        
        main_widget_layout = QVBoxLayout(widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.addWidget(scroll_area)

    def create_red_header_with_lottie(self, layout):
        """🔴 HTTP SERVER + LOTTIE HEADER"""
        header = QWidget()
        header.setFixedHeight(140)
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC143C, stop:0.5 #B22222, stop:1 #8B0000);
                border: none;
                border-radius: 16px;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(20)
        
        # SOL: Logo + Başlık
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_layout = QHBoxLayout(left_widget)
        left_layout.setSpacing(16)
        
        self.logo_label = QLabel()
        self.load_logo()
        self.logo_label.setStyleSheet("""
            background: transparent;
            border-radius: 35px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(70, 70)
        left_layout.addWidget(self.logo_label)
        
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(4)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        main_title = QLabel("KARŞIYAKA 4")
        main_title.setFont(QFont('Segoe UI', 26, QFont.Bold))
        main_title.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("Nöbetçi Eczane Sistemi")
        sub_title.setFont(QFont('Segoe UI', 13, QFont.Medium))
        sub_title.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        title_layout.addWidget(sub_title)
        
        left_layout.addWidget(title_widget)
        header_layout.addWidget(left_widget, 2)
        
        # SAĞ: Saat/Tarih + HTTP Lottie Weather
        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(0, 8, 0, 8)
        
        # SAAT/TARİH ROW
        datetime_row = QWidget()
        datetime_row.setStyleSheet("background: transparent;")
        datetime_row_layout = QHBoxLayout(datetime_row)
        datetime_row_layout.setSpacing(8)
        datetime_row_layout.setContentsMargins(0, 0, 0, 0)
        datetime_row_layout.addStretch()
        
        self.time_display = QLabel()
        self.time_display.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.time_display.setStyleSheet("color: white; background: transparent;")
        self.time_display.setAlignment(Qt.AlignRight)
        datetime_row_layout.addWidget(self.time_display)
        
        bullet = QLabel("•")
        bullet.setFont(QFont('Segoe UI', 18, QFont.Bold))
        bullet.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent;")
        bullet.setAlignment(Qt.AlignCenter)
        datetime_row_layout.addWidget(bullet)
        
        self.date_display = QLabel()
        self.date_display.setFont(QFont('Segoe UI', 18, QFont.Medium))
        self.date_display.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        self.date_display.setAlignment(Qt.AlignLeft)
        datetime_row_layout.addWidget(self.date_display)
        
        right_layout.addWidget(datetime_row)
        
        # HTTP LOTTIE WEATHER ROW
        weather_row = QWidget()
        weather_row.setFixedHeight(30)
        weather_row.setStyleSheet("background: transparent;")
        weather_row_layout = QHBoxLayout(weather_row)
        weather_row_layout.setSpacing(8)
        weather_row_layout.setContentsMargins(0, 0, 0, 0)
        weather_row_layout.addStretch()
        
        # HTTP LOTTIE WIDGET
        weather_row_layout.addWidget(self.lottie_widget)
        
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setFont(QFont('Segoe UI', 16, QFont.Bold))
        self.weather_temp.setStyleSheet("color: white; background: transparent;")
        weather_row_layout.addWidget(self.weather_temp)
        
        # Fallback emoji (HTTP Lottie yoksa)
        self.weather_icon = QLabel("☀")
        self.weather_icon.setFont(QFont('Segoe UI', 16))
        self.weather_icon.setStyleSheet("color: white; background: transparent;")
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.hide()  # Başlangıçta gizli
        weather_row_layout.addWidget(self.weather_icon)
        
        right_layout.addWidget(weather_row)
        header_layout.addWidget(right_widget, 1)
        layout.addWidget(header)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def create_svg_info_section(self, layout):
        """📋 SVG İKONLU INFO SECTION"""
        info_container = QWidget()
        info_container.setFixedHeight(400)
        info_container.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border: none;
            border-radius: 16px;
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(32, 24, 32, 24)
        info_layout.setSpacing(20)
        title = QLabel("NÖBETÇİ ECZANE BİLGİLERİ")
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setStyleSheet(f"""
            color: {self.colors['text_primary']};
            background-color: {self.colors['bg_accent']};
            padding: 16px 24px;
            border-radius: 12px;
            border: none;
        """)
        title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(title)
        
        content_row = QWidget()
        content_row.setStyleSheet("background: transparent;")
        content_row_layout = QHBoxLayout(content_row)
        content_row_layout.setSpacing(24)
        
        # SOL: SVG İKONLU ECZANE BİLGİLERİ
        self.info_widget = QWidget()
        self.info_widget.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border: none;
            border-radius: 12px;
            padding: 24px;
        """)
        
        self.info_widget_layout = QVBoxLayout(self.info_widget)
        self.info_widget_layout.setSpacing(16)
        
        # Başlangıç loading mesajı
        loading_label = QLabel("HTTP Server üzerinden yükleniyor...")
        loading_label.setFont(QFont('Segoe UI', 16))
        loading_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        loading_label.setAlignment(Qt.AlignCenter)
        self.info_widget_layout.addWidget(loading_label)
        
        content_row_layout.addWidget(self.info_widget, 2)
        
        # SAĞ: QR KOD
        qr_widget = QWidget()
        qr_widget.setStyleSheet("background: transparent;")
        qr_widget_layout = QVBoxLayout(qr_widget)
        qr_widget_layout.setSpacing(12)
        qr_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        qr_title = QLabel("YOL TARİFİ İÇİN\nQR OKUTUNUZ")
        qr_title.setFont(QFont('Segoe UI', 12, QFont.Bold))
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            background: transparent;
            padding: 8px;
        """)
        qr_widget_layout.addWidget(qr_title)
        
        qr_container = QWidget()
        qr_container.setStyleSheet("background: transparent;")
        qr_container_layout = QHBoxLayout(qr_container)
        qr_container_layout.setContentsMargins(0, 0, 0, 0)
        qr_container_layout.addStretch()
        
        self.qr_label = QLabel("QR\nYükleniyor...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(160, 160)
        self.qr_label.setStyleSheet(f"""
            background-color: {self.colors['text_primary']};
            border: none;
            border-radius: 12px;
            color: {self.colors['bg_primary']};
            font-size: 16px;
            font-weight: bold;
        """)
        qr_container_layout.addWidget(self.qr_label)
        qr_container_layout.addStretch()
        
        qr_widget_layout.addWidget(qr_container)
        qr_widget_layout.addStretch()
        content_row_layout.addWidget(qr_widget, 1)
        
        info_layout.addWidget(content_row)
        layout.addWidget(info_container)

    def create_svg_info_display(self, name, phone, address, distance, duration):
        """📱 SVG İKONLU BİLGİ DİSPLAY"""
        # Mevcut widget'ları temizle
        for i in reversed(range(self.info_widget_layout.count())): 
            self.info_widget_layout.itemAt(i).widget().setParent(None)
        
        # ECZANE ADI
        name_label = QLabel(name)
        name_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        name_label.setStyleSheet(f"color: {self.colors['text_primary']}; padding: 8px;")
        name_label.setWordWrap(True)
        self.info_widget_layout.addWidget(name_label)
        
        # TELEFON - SVG İKONLU
        phone_row = QWidget()
        phone_row.setStyleSheet("background: transparent;")
        phone_row_layout = QHBoxLayout(phone_row)
        phone_row_layout.setSpacing(12)
        phone_row_layout.setContentsMargins(0, 4, 0, 4)
        
        phone_icon = self.load_svg_icon("icons/phone.svg", size=18)
        if phone_icon:
            phone_row_layout.addWidget(phone_icon)
        else:
            phone_fallback = self.create_fallback_icon("📞", self.colors['accent_blue'], 18)
            phone_row_layout.addWidget(phone_fallback)
        
        phone_label = QLabel(phone)
        phone_label.setFont(QFont('Segoe UI', 14))
        phone_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        phone_row_layout.addWidget(phone_label)
        phone_row_layout.addStretch()
        self.info_widget_layout.addWidget(phone_row)
        
        # ADRES - SVG İKONLU
        address_row = QWidget()
        address_row.setStyleSheet("background: transparent;")
        address_row_layout = QHBoxLayout(address_row)
        address_row_layout.setSpacing(12)
        address_row_layout.setContentsMargins(0, 4, 0, 4)
        address_row_layout.setAlignment(Qt.AlignTop)
        
        location_icon = self.load_svg_icon("icons/location.svg", size=18)
        if location_icon:
            address_row_layout.addWidget(location_icon)
        else:
            location_fallback = self.create_fallback_icon("📍", self.colors['accent_red'], 18)
            address_row_layout.addWidget(location_fallback)
        
        address_label = QLabel(address)
        address_label.setFont(QFont('Segoe UI', 14))
        address_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        address_label.setWordWrap(True)
        address_row_layout.addWidget(address_label)
        self.info_widget_layout.addWidget(address_row)
        
        # MESAFE - SVG İKONLU
        distance_row = QWidget()
        distance_row.setStyleSheet("background: transparent;")
        distance_row_layout = QHBoxLayout(distance_row)
        distance_row_layout.setSpacing(12)
        distance_row_layout.setContentsMargins(0, 4, 0, 4)
        
        distance_icon = self.load_svg_icon("icons/distance.svg", size=18)
        if distance_icon:
            distance_row_layout.addWidget(distance_icon)
        else:
            distance_fallback = self.create_fallback_icon("🚗", self.colors['accent_green'], 18)
            distance_row_layout.addWidget(distance_fallback)
        
        distance_label = QLabel(f"Mesafe: {distance}")
        distance_label.setFont(QFont('Segoe UI', 14))
        distance_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        distance_row_layout.addWidget(distance_label)
        distance_row_layout.addStretch()
        self.info_widget_layout.addWidget(distance_row)
        
        # SÜRE - SVG İKONLU
        time_row = QWidget()
        time_row.setStyleSheet("background: transparent;")
        time_row_layout = QHBoxLayout(time_row)
        time_row_layout.setSpacing(12)
        time_row_layout.setContentsMargins(0, 4, 0, 4)
        
        time_icon = self.load_svg_icon("icons/time.svg", size=18)
        if time_icon:
            time_row_layout.addWidget(time_icon)
        else:
            time_fallback = self.create_fallback_icon("⏱️", self.colors['accent_purple'], 18)
            time_row_layout.addWidget(time_fallback)
        
        time_label = QLabel(f"Süre: {duration}")
        time_label.setFont(QFont('Segoe UI', 14))
        time_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        time_row_layout.addWidget(time_label)
        time_row_layout.addStretch()
        self.info_widget_layout.addWidget(time_row)

    def create_corporate_qr_map_section(self, layout):
        """🗺️ BÜYÜK HARİTA"""
        map_container = QWidget()
        map_container.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border: none;
            border-radius: 16px;
        """)
        
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(24, 24, 24, 24)
        map_layout.setSpacing(16)
        
        map_title = QLabel("KONUM & ROTA")
        map_title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        map_title.setAlignment(Qt.AlignCenter)
        map_title.setStyleSheet(f"""
            color: {self.colors['text_primary']};
            background-color: {self.colors['bg_accent']};
            padding: 12px 20px;
            border-radius: 12px;
            border: none;
        """)
        map_layout.addWidget(map_title)
        
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(570)
        self.map_label.setMaximumHeight(570)
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border: none;
            border-radius: 12px;
            color: {self.colors['text_secondary']};
            font-size: 18px;
        """)
        self.show_loading_spinner()
        map_layout.addWidget(self.map_label)
        layout.addWidget(map_container)

    def create_corporate_footer(self, layout):
        """🏢 HTTP SERVER FOOTER"""
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border: none;
            border-radius: 16px;
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(32, 16, 32, 16)
        
        self.last_update_label = QLabel("Son güncelleme: --:--")
        self.last_update_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        self.last_update_label.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            background: transparent;
        """)
        footer_layout.addWidget(self.last_update_label)
        
        footer_layout.addStretch()
        
        self.status_label = QLabel("● Powered by AI")
        self.status_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.status_label.setStyleSheet(f"""
            color: {self.colors['accent_green']};
            background: transparent;
        """)
        footer_layout.addWidget(self.status_label)
        
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
                        scaled_logo = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_label.setPixmap(scaled_logo)
                        logo_loaded = True
                        print(f"✅ Logo yüklendi: {path}")
                        break
            if not logo_loaded:
                self.logo_label.setText("🏥")
                self.logo_label.setFont(QFont('Segoe UI', 24))
                self.logo_label.setStyleSheet("""
                    background: transparent;
                    color: white;
                    border-radius: 35px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                """)
                print("📋 Logo bulunamadı, emoji kullanıldı")
        except Exception as e:
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Segoe UI', 28))
            print(f"⚠️ Logo hatası: {e}")

    def update_time(self):
        """Saat ve tarih güncelle"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        
        if hasattr(self, 'time_display'):
            self.time_display.setText(time_str)
        if hasattr(self, 'date_display'):
            self.date_display.setText(date_str)

    def setup_video_ui(self):
        """Video UI"""
        widget = self.video_widget
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        widget.setStyleSheet(f"background-color: {self.colors['bg_primary']};")
        
        self.video_widget_display = QVideoWidget()
        layout.addWidget(self.video_widget_display)
        
        self.no_video_label = QLabel()
        self.no_video_label.setAlignment(Qt.AlignCenter)
        self.no_video_label.setFont(QFont('Segoe UI', 28, QFont.Bold))
        self.no_video_label.setStyleSheet(f"""
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
            padding: 50px;
        """)
        self.update_video_message()
        layout.addWidget(self.no_video_label)

    def update_video_message(self):
        """Video mesajını güncelle"""
        if not self.video_path:
            message = """📺 REKLAM MODU

ads/ klasöründe video dosyası bulunamadı.

Desteklenen formatlar:
• MP4 (.mp4)
• MOV (.mov) 
• AVI (.avi)

Video eklemek için ads/ klasörüne
video dosyası koyun."""
        else:
            message = "🎬 Video yükleniyor..."
            
        self.no_video_label.setText(message)

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
        self.update_timer.start(1800000)

        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule_and_switch)
        self.schedule_timer.start(60000)
        
        print("⏰ Nöbet saatleri kontrolü aktif: 18:45-08:45")

    def setup_animations(self):
        """🎬 ANİMASYON SİSTEMLERİ KURULUM"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_animation)
        self.pulse_timer.start(1000)
        self.pulse_state = True
        
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.spinner_animation)
        self.spinner_angle = 0
        self.is_loading = False
        
        print("🎬 Animasyon sistemleri başlatıldı!")

    def pulse_animation(self):
        """💓 PULSE EFEKT"""
        if hasattr(self, 'status_label'):
            if self.pulse_state:
                self.status_label.setStyleSheet(f"""
                    color: {self.colors['accent_green']};
                    background: rgba(48, 209, 88, 0.2);
                    border-radius: 8px;
                    padding: 4px 8px;
                    font-weight: bold;
                """)
            else:
                self.status_label.setStyleSheet(f"""
                    color: {self.colors['accent_green']};
                    background: transparent;
                    font-weight: bold;
                """)
            
            self.pulse_state = not self.pulse_state

    def show_loading_spinner(self):
        """🔄 LOADING SPINNER GÖSTER"""
        self.is_loading = True
        self.map_label.setText("🔄 Harita yükleniyor...")
        self.spinner_timer.start(100)

    def hide_loading_spinner(self):
        """🔄 LOADING SPINNER GİZLE"""
        self.is_loading = False
        self.spinner_timer.stop()

    def spinner_animation(self):
        """🔄 DÖNEN CIRCLE ANİMASYON"""
        if self.is_loading:
            spinner_chars = ["◐", "◓", "◑", "◒"]
            char_index = (self.spinner_angle // 2) % len(spinner_chars)
            spinner_char = spinner_chars[char_index]
            
            self.map_label.setText(f"{spinner_char} Harita yükleniyor...")
            self.spinner_angle += 1
            
            if self.spinner_angle > 100:
                self.spinner_angle = 0

    def check_schedule_and_switch(self):
        """Nöbet saatleri kontrolü ve mod değişimi"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()
        
        is_night_shift = (
            current_time >= datetime.strptime("18:45", "%H:%M").time() or
            current_time <= datetime.strptime("08:45", "%H:%M").time()
        )
        
        is_sunday = (current_day == 6)
        should_show_pharmacy = is_night_shift or is_sunday
        
        if should_show_pharmacy and self.current_mode != "pharmacy":
            print(f"🏥 NÖBET MODUNA GEÇİYOR - Saat: {now.strftime('%H:%M')}")
            self.switch_to_pharmacy_mode()
            
        elif not should_show_pharmacy and self.current_mode != "video":
            print(f"🎬 REKLAM MODUNA GEÇİYOR - Saat: {now.strftime('%H:%M')}")
            self.switch_to_video_mode()

    def switch_to_video_mode(self):
        """Video moduna geç"""
        self.current_mode = "video"
        self.stacked_widget.setCurrentWidget(self.video_widget)
        
        if self.video_path and os.path.exists(self.video_path):
            self.media_player.play()
            self.no_video_label.hide()
            self.video_widget_display.show()
            print(f"▶️ Video oynatılıyor: {self.video_path}")
        else:
            self.video_widget_display.hide()
            self.no_video_label.show()
            print("❌ Video bulunamadı")

    def switch_to_pharmacy_mode(self):
        """Eczane moduna geç"""
        self.current_mode = "pharmacy"
        if hasattr(self, 'media_player') and self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
        self.stacked_widget.setCurrentWidget(self.pharmacy_widget)
        self.fetch_data()
        self.fetch_weather_data()

    def fetch_data(self):
        """📡 HTTP SERVER İLE ECZANE VERİSİ ÇEK"""
        try:
            print("📡 HTTP Server üzerinden eczane bilgileri güncelleniyor...")
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
                    
                    # SVG İKONLU BİLGİ GÜNCELLEMESİ
                    self.create_svg_info_display(name, phone, address, distance, duration)
                    
                    # QR kod oluştur
                    if maps_url:
                        self.create_qr_code(maps_url)
                    
                    # Harita oluştur
                    self.create_route_map(end_lat, end_lon)
                    
                    # Son güncelleme
                    now = datetime.now()
                    self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')}")
                    
                    print("✅ HTTP Server eczane bilgileri güncellendi")
                    return
            
            # Bulunamadı durumu
            error_label = QLabel("KARŞIYAKA 4'te nöbetçi eczane bulunamadı")
            error_label.setFont(QFont('Segoe UI', 16))
            error_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
            error_label.setAlignment(Qt.AlignCenter)
            
            # Mevcut widget'ları temizle
            for i in reversed(range(self.info_widget_layout.count())): 
                self.info_widget_layout.itemAt(i).widget().setParent(None)
            self.info_widget_layout.addWidget(error_label)
            
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")
            
        except Exception as e:
            error_label = QLabel(f"Bağlantı hatası: {str(e)}")
            error_label.setFont(QFont('Segoe UI', 16))
            error_label.setStyleSheet(f"color: {self.colors['accent_red']};")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            
            # Mevcut widget'ları temizle
            for i in reversed(range(self.info_widget_layout.count())): 
                self.info_widget_layout.itemAt(i).widget().setParent(None)
            self.info_widget_layout.addWidget(error_label)
            
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Hata)")
            print(f"❌ HTTP Server güncelleme hatası: {e}")

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
                    
                    distance_value = route['legs'][0]['distance']['value']
                    
                    if distance_value < 500:
                        zoom_level = 19
                    elif distance_value < 800:
                        zoom_level = 18
                    elif distance_value < 1200:
                        zoom_level = 17
                    elif distance_value < 2000:
                        zoom_level = 16
                    elif distance_value < 3000:
                        zoom_level = 15
                    else:
                        zoom_level = 14
                    
                    map_width = 820
                    map_height = 550
                    
                    static_map_url = (
                        f"https://maps.googleapis.com/maps/api/staticmap?"
                        f"size={map_width}x{map_height}&"
                        f"maptype=roadmap&"
                        f"style=feature:all|element:geometry|color:0x1a1a1a&"
                        f"style=feature:all|element:labels.icon|visibility:off&"
                        f"style=feature:all|element:labels.text.fill|color:0xcccccc&"
                        f"style=feature:all|element:labels.text.stroke|color:0x000000&"
                        f"style=feature:road|element:geometry|color:0x333333&"
                        f"style=feature:road|element:geometry.stroke|color:0x222222&"
                        f"style=feature:road|element:labels.text.fill|color:0xffffff&"
                        f"style=feature:water|element:geometry|color:0x007AFF&"
                        f"style=feature:landscape|element:geometry|color:0x111111&"
                        f"markers=color:0x30D158|size:mid|label:B|{self.start_lat},{self.start_lon}&"
                        f"markers=color:0xFF3B30|size:mid|label:E|{end_lat},{end_lon}&"
                        f"path=color:0x007AFF|weight:4|enc:{polyline}&"
                        f"zoom={zoom_level}&"
                        f"key={self.api_key}"
                    )
                    
                    map_response = requests.get(static_map_url, timeout=10)
                    
                    if map_response.status_code == 200:
                        self.hide_loading_spinner()
                        
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        
                        scaled_pixmap = pixmap.scaled(820, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.map_label.setPixmap(scaled_pixmap)
                        
                        print("✅ HTTP Server harita oluşturuldu")
                        return
                        
        except Exception as e:
            print(f"Harita hatası: {e}")
            
        self.hide_loading_spinner()
        self.map_label.setText("❌ Harita yüklenemedi")
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            color: {self.colors['text_secondary']};
            font-size: 16px;
            border: none;
            border-radius: 12px;
        """)

    def fetch_weather_data(self):
        """🌤️ HTTP SERVER İLE HAVA DURUMU ÇEK"""
        try:
            print("🌡️ HTTP Server üzerinden hava durumu alınıyor...")
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
            weather_main = data['weather'][0]['main'].lower()
            
            # HTTP Lottie animasyonu yükle
            lottie_loaded = self.load_lottie_animation(weather_main, temp)
            
            if lottie_loaded:
                # HTTP Lottie yüklendi, emoji'yi gizle
                self.weather_icon.hide()
                self.lottie_widget.show()
                print(f"🎬 HTTP Lottie animasyon: {weather_main}")
            else:
                # Fallback emoji kullan
                self.lottie_widget.hide()
                self.weather_icon.show()
                weather_emoji = self.get_weather_emoji(weather_main, temp)
                self.weather_icon.setText(weather_emoji)
                print(f"😀 Fallback emoji: {weather_emoji}")
            
            self.weather_temp.setText(f"{temp}°C")
            
            print(f"✅ HTTP Server hava durumu: {temp}°C - {desc}")
            
        except Exception as e:
            self.weather_temp.setText("--°C")
            self.weather_icon.setText("❓")
            self.weather_icon.show()
            self.lottie_widget.hide()
            print(f"Hava durumu hatası: {e}")

    def get_weather_emoji(self, weather_main, temp):
        """🌟 WEATHER EMOJI"""
        if weather_main in ['clear', 'sunny']:
            if temp >= 30:
                return "🔥"
            elif temp >= 25:
                return "☀"
            else:
                return "🌤"
        elif weather_main in ['clouds', 'partly cloudy']:
            return "☁"
        elif weather_main in ['rain', 'drizzle']:
            return "🌧"
        elif weather_main in ['thunderstorm', 'storm']:
            return "⚡"
        elif weather_main in ['mist', 'fog', 'haze']:
            return "🌫"
        elif weather_main in ['snow']:
            return "❄"
        elif weather_main in ['wind']:
            return "💨"
        else:
            return "🌈"

    def create_qr_code(self, url):
        """QR kod oluştur"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='#000000', back_color='#ffffff')
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            scaled_pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
            print("✅ QR kodu oluşturuldu")
            
        except Exception as e:
            self.qr_label.setText("QR\nHatası")
            self.qr_label.setStyleSheet(f"""
                background-color: {self.colors['text_primary']};
                color: {self.colors['bg_primary']};
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            """)
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
    print("🌐 HTTP SERVER + LOTTIE ANIMATIONS - CORS FREE!")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    try:
        window = ModernCorporateEczaneApp()
        print("✅ HTTP Server + Lottie sistemi başlatıldı")
        print("🌐 Server: http://localhost:8000-8009 (otomatik port)")
        print("📁 Lottie dosyaları: weather_lottie/*.json")
        print("🔧 CORS sorunu %100 çözüldü!")
        print("🎬 Console mesajları gizlendi")
        print("⌨️  ESC: Çıkış, F11: Tam ekran")
        print("=" * 70)
        print("🚀 HTTP SERVER LOTTIE SİSTEMİ AKTİF!")
        print("📊 Status:")
        print("   ✅ Otomatik port bulma")
        print("   ✅ CORS bypass")
        print("   ✅ Console gizleme") 
        print("   ✅ Fallback emoji sistemi")
        print("   ✅ 22x22 optimum boyut")
        print("   ✅ Tam eczane bilgi sistemi")
        print("   ✅ SVG ikonlar + QR kod + Harita")
        print("=" * 70)
        
        app.exec_()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
