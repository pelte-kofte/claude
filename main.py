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


# ============================================================================
# 🔄 WORKER THREAD - ANA THREAD'İ DONDURMAMAK İÇİN
# ============================================================================
class DataFetchWorker(QThread):
    """🔄 Arka planda veri çeken worker thread"""
    
    # Sinyaller - UI güncellemesi için
    pharmacy_data_ready = pyqtSignal(dict)
    weather_data_ready = pyqtSignal(dict)
    map_data_ready = pyqtSignal(dict)  # bytes değil dict - mesafe/süre bilgisi de var
    error_occurred = pyqtSignal(str)
    
    def __init__(self, task_type, **kwargs):
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs
        
    def run(self):
        """Thread'de çalışacak kod"""
        try:
            if self.task_type == "pharmacy":
                self.fetch_pharmacy_data()
            elif self.task_type == "weather":
                self.fetch_weather_data()
            elif self.task_type == "map":
                self.fetch_map_data()
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def fetch_pharmacy_data(self):
        """📡 Eczane verisi çek"""
        try:
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            r = requests.get(url, timeout=15)
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
                    
                    # Google Maps URL
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
                    
                    # Veriyi gönder
                    data = {
                        'found': True,
                        'name': name,
                        'phone': phone,
                        'address': address,
                        'maps_url': maps_url,
                        'end_lat': end_lat,
                        'end_lon': end_lon
                    }
                    self.pharmacy_data_ready.emit(data)
                    return
            
            # Bulunamadı
            self.pharmacy_data_ready.emit({'found': False})
            
        except Exception as e:
            self.error_occurred.emit(f"Eczane verisi hatası: {e}")
    
    def fetch_weather_data(self):
        """🌤️ Hava durumu çek"""
        try:
            api_key = self.kwargs.get('api_key')
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': 'Izmir,TR',
                'appid': api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'weather_main': data['weather'][0]['main'].lower()
            }
            self.weather_data_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"Hava durumu hatası: {e}")
    
    def fetch_map_data(self):
        """🗺️ Harita verisi çek"""
        try:
            api_key = self.kwargs.get('api_key')
            start_lat = self.kwargs.get('start_lat')
            start_lon = self.kwargs.get('start_lon')
            end_lat = self.kwargs.get('end_lat')
            end_lon = self.kwargs.get('end_lon')
            
            # Directions API
            directions_url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={start_lat},{start_lon}&"
                f"destination={end_lat},{end_lon}&"
                f"mode=driving&"
                f"key={api_key}"
            )
            
            directions_response = requests.get(directions_url, timeout=15)
            
            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                
                if directions_data['status'] == 'OK':
                    route = directions_data['routes'][0]
                    polyline = route['overview_polyline']['points']
                    
                    # Mesafe ve süre
                    leg = route['legs'][0]
                    distance = leg['distance']['text']
                    duration = leg['duration']['text']
                    
                    # Türkçeleştir
                    duration = duration.replace('mins', 'dakika').replace('min', 'dakika')
                    duration = duration.replace('hours', 'saat').replace('hour', 'saat')
                    
                    map_width = 820
                    map_height = 550
                    
                    # Static Map URL - ZOOM YOK, OTOMATİK FIT
                    # Google Maps markers ve path'e göre otomatik zoom yapar
                    static_map_url = (
                        f"https://maps.googleapis.com/maps/api/staticmap?"
                        f"size={map_width}x{map_height}&"
                        f"maptype=roadmap&"
                        f"visible={start_lat},{start_lon}|{end_lat},{end_lon}&"
                        f"markers=color:blue|size:mid|label:B|{start_lat},{start_lon}&"
                        f"markers=color:red|size:mid|label:E|{end_lat},{end_lon}&"
                        f"path=color:0x007AFF|weight:5|enc:{polyline}&"
                        f"key={api_key}"
                    )
                    
                    map_response = requests.get(static_map_url, timeout=15)
                    
                    if map_response.status_code == 200:
                        # Harita + mesafe/süre bilgisini gönder
                        result = {
                            'map_data': map_response.content,
                            'distance': distance,
                            'duration': duration
                        }
                        self.map_data_ready.emit(result)
                        return
            
            self.error_occurred.emit("Harita oluşturulamadı")
            
        except Exception as e:
            self.error_occurred.emit(f"Harita hatası: {e}")


# ============================================================================
# 🌐 CORS HTTP SERVER
# ============================================================================
class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """🌐 CORS BYPASS HANDLER"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """HTTP loglarını gizle"""
        pass


# ============================================================================
# 🏥 ANA UYGULAMA
# ============================================================================
class ModernCorporateEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane")
        
        # DİKEY MONİTÖR İÇİN BOYUTLAR
        self.setFixedSize(900, 1280)
        
        # 🌐 LOCAL HTTP SERVER BAŞLAT
        self.start_local_server()
        
        # API anahtarları - Environment variable'dan al (güvenlik için)
        self.api_key = os.environ.get('GOOGLE_MAPS_KEY', "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE")
        self.weather_api_key = os.environ.get('OPENWEATHER_KEY', "b0d1be7721b4967d8feb810424bd9b6f")
        
        # Başlangıç koordinatları (Eczanenin konumu)
        self.start_lat = 38.47434762293852
        self.start_lon = 27.112356625119595
        
        # Eczane koordinatları (güncellenecek)
        self.end_lat = None
        self.end_lon = None
        
        self.current_mode = None
        self.video_path = None
        
        # Worker thread referansları
        self.pharmacy_worker = None
        self.weather_worker = None
        self.map_worker = None
        
        # 🎨 MODERN CORPORATE RENK PALETİ
        self.colors = {
            'bg_primary': '#000000',
            'bg_secondary': '#000000',
            'bg_card': '#000000',
            'bg_accent': '#000000',
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
        print("🎬 Uygulama başlatıldı!")

    def start_local_server(self):
        """🌐 CORS BYPASS HTTP SERVER"""
        self.server_port = 8000
        self.server_url = f"http://localhost:{self.server_port}"
        self.server_ready = False
        
        def run_server():
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                os.chdir(current_dir)
                print(f"📁 Server dizini: {current_dir}")
                
                handler = CORSHTTPRequestHandler
                
                for port in range(8000, 8010):
                    try:
                        with socketserver.TCPServer(("", port), handler) as httpd:
                            self.server_port = port
                            self.server_url = f"http://localhost:{port}"
                            print(f"🌐 HTTP Server: {self.server_url}")
                            self.server_ready = True
                            httpd.serve_forever()
                            break
                    except OSError:
                        continue
                        
            except Exception as e:
                print(f"❌ Server hatası: {e}")
                self.server_ready = False
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        QTimer.singleShot(1500, self.check_server_ready)

    def check_server_ready(self):
        """Server hazır kontrolü"""
        if self.server_ready:
            print("✅ HTTP Server hazır!")
        else:
            QTimer.singleShot(500, self.check_server_ready)

    def setup_lottie_weather(self):
        """🎬 LOTTIE SİSTEMİ"""
        self.lottie_widget = QWebEngineView()
        self.lottie_widget.setFixedSize(40, 40)
        
        self.lottie_widget.setStyleSheet("""
            QWebEngineView {
                background: transparent !important;
                border: none;
            }
        """)
        
        page = self.lottie_widget.page()
        page.setBackgroundColor(QColor(0, 0, 0, 0))
        page.javaScriptConsoleMessage = lambda *args: None
        
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

    def load_lottie_animation(self, weather_main, temp=25):
        """🌈 LOTTIE YÜKLE"""
        try:
            if not self.server_ready:
                return False
            
            lottie_file = None
            
            if weather_main in ['clear', 'sunny']:
                lottie_file = self.lottie_files.get('hot') if temp >= 30 else self.lottie_files.get('sunny')
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
            
            if lottie_file and os.path.exists(lottie_file):
                http_url = f"{self.server_url}/{lottie_file}"
                
                html_content = f"""
                <!DOCTYPE html>
                <html style="background: transparent;">
                <head>
                    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
                    <style>
                        * {{ margin: 0 !important; padding: 0 !important; background: transparent !important; }}
                        html, body {{ background: transparent !important; overflow: hidden; }}
                        lottie-player {{ width: 36px !important; height: 36px !important; background: transparent !important; }}
                    </style>
                </head>
                <body style="background: transparent !important;">
                    <lottie-player src="{http_url}" background="transparent" speed="1" loop autoplay></lottie-player>
                </body>
                </html>
                """
                
                self.lottie_widget.setHtml(html_content)
                return True
                
            return False
                
        except Exception as e:
            print(f"❌ Lottie hatası: {e}")
            return False

    def load_svg_icon(self, icon_path, size=24):
        """🎨 SVG İkon Yükleyici"""
        try:
            if os.path.exists(icon_path):
                svg_widget = QSvgWidget(icon_path)
                svg_widget.setFixedSize(size, size)
                svg_widget.setStyleSheet("background: transparent;")
                return svg_widget
            return None
        except:
            return None

    def create_fallback_icon(self, emoji, color="#ffffff", size=20):
        """🔄 FALLBACK EMOJI İKON"""
        label = QLabel(emoji)
        label.setFont(QFont('Geist', size-4))
        label.setStyleSheet(f"color: {color}; background: transparent;")
        label.setFixedSize(size, size)
        label.setAlignment(Qt.AlignCenter)
        return label

    def setup_ui(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.pharmacy_widget = QWidget()
        self.setup_pharmacy_ui()
        self.stacked_widget.addWidget(self.pharmacy_widget)
        
        self.video_widget = QWidget()
        self.setup_video_ui()
        self.stacked_widget.addWidget(self.video_widget)

    def setup_pharmacy_ui(self):
        """🏢 PHARMACY UI"""
        widget = self.pharmacy_widget
        
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_primary']};
                font-family: 'Geist', 'Helvetica Neue', sans-serif;
                color: {self.colors['text_primary']};
                border: none;
            }}
            QLabel {{
                border: none;
            }}
            QFrame {{
                    border: none;
            }}
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                background: {self.colors['bg_card']};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors['accent_blue']};
                border-radius: 4px;
                min-height: 30px;
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
        """🔴 HEADER"""
        header = QWidget()
        header.setFixedHeight(140)
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC143C, stop:0.5 #B22222, stop:1 #8B0000);
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
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(90, 90)
        left_layout.addWidget(self.logo_label)
        
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(4)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        main_title = QLabel("KARŞIYAKA 4")
        main_title.setFont(QFont('Geist', 26, QFont.Normal))
        main_title.setStyleSheet("color: white; background: transparent;")
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("Nöbetçi Eczane Sistemi")
        sub_title.setFont(QFont('Geist', 13, QFont.Normal))
        sub_title.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        title_layout.addWidget(sub_title)
        
        left_layout.addWidget(title_widget)
        header_layout.addWidget(left_widget, 2)
        
        # SAĞ: Saat/Tarih + Weather
        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(0, 8, 0, 8)
        
        # Saat/Tarih satırı
        datetime_row = QWidget()
        datetime_row.setStyleSheet("background: transparent;")
        datetime_row_layout = QHBoxLayout(datetime_row)
        datetime_row_layout.setSpacing(8)
        datetime_row_layout.setContentsMargins(0, 0, 0, 0)
        datetime_row_layout.addStretch()
        
        self.time_display = QLabel()
        self.time_display.setFont(QFont('Geist', 18, QFont.Normal))
        self.time_display.setStyleSheet("color: white; background: transparent;")
        datetime_row_layout.addWidget(self.time_display)
        
        bullet = QLabel("•")
        bullet.setFont(QFont('Geist', 18, QFont.Normal))
        bullet.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent; padding-bottom: 1px;")
        datetime_row_layout.addWidget(bullet)
        
        self.date_display = QLabel()
        self.date_display.setFont(QFont('Geist', 18, QFont.Normal))
        self.date_display.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        datetime_row_layout.addWidget(self.date_display)
        
        right_layout.addWidget(datetime_row)
        
        # Weather satırı
        weather_row = QWidget()
        weather_row.setFixedHeight(30)
        weather_row.setStyleSheet("background: transparent; border: none;")
        weather_row_layout = QHBoxLayout(weather_row)
        weather_row_layout.setSpacing(8)
        weather_row_layout.setContentsMargins(0, 0, 0, 0)
        weather_row_layout.addStretch()
        
        weather_row_layout.addWidget(self.lottie_widget)
        
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setFont(QFont('Geist', 16, QFont.Normal))
        self.weather_temp.setStyleSheet("color: white; background: transparent; none;")
        weather_row_layout.addWidget(self.weather_temp)
        
        self.weather_icon = QLabel("☀")
        self.weather_icon.setFont(QFont('Geist', 16))
        self.weather_icon.setStyleSheet("color: white; background: transparent;")
        self.weather_icon.hide()
        weather_row_layout.addWidget(self.weather_icon)
        
        right_layout.addWidget(weather_row)
        header_layout.addWidget(right_widget, 1)
        layout.addWidget(header)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def create_svg_info_section(self, layout):
        """📋 INFO SECTION"""
        info_container = QWidget()
        info_container.setFixedHeight(400)
        info_container.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border-radius: 16px;
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(32, 24, 32, 24)
        info_layout.setSpacing(20)
        
        title = QLabel("NÖBETÇİ ECZANE BİLGİLERİ")
        title.setFont(QFont('Geist', 20, QFont.Normal))
        title.setStyleSheet(f"""
            color: {self.colors['text_primary']};
            background-color: {self.colors['bg_accent']};
            padding: 16px 24px;
            border-radius: 12px;
        """)
        title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(title)
        
        content_row = QWidget()
        content_row.setStyleSheet("background: transparent;")
        content_row_layout = QHBoxLayout(content_row)
        content_row_layout.setSpacing(24)
        
        # SOL: Eczane bilgileri
        self.info_widget = QWidget()
        self.info_widget.setObjectName("infoWidget")
        self.info_widget.setStyleSheet("""
            QWidget#infoWidget {
                background: #141414;
                border: 0.5px solid #333333;
                border-radius: 12px;
            }
            QWidget#infoWidget > QWidget {
                border: none;
            }
            QWidget#infoWidget QLabel {
                border: none;
            }
        """)
        
        self.info_widget_layout = QVBoxLayout(self.info_widget)
        self.info_widget_layout.setSpacing(16)
        
        loading_label = QLabel("⏳ Yükleniyor...")
        loading_label.setFont(QFont('Geist', 16))
        loading_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        loading_label.setAlignment(Qt.AlignCenter)
        self.info_widget_layout.addWidget(loading_label)
        
        content_row_layout.addWidget(self.info_widget, 2)
        
        # SAĞ: QR Kod
        qr_widget = QWidget()
        qr_widget.setObjectName("qrWidget")
        qr_widget.setStyleSheet("""
            QWidget#qrWidget {
                background: #141414;
                border: 0.5px solid #333333;
                border-radius: 12px;
            }
            QWidget#qrWidget > QWidget {
                border: none;
            }
            QWidget#qrWidget QLabel {
                border: none;
            }
        """)
        qr_widget_layout = QVBoxLayout(qr_widget)
        qr_widget_layout.setSpacing(12)
        qr_widget_layout.setContentsMargins(0, 0, 0, 0)
        
        qr_title = QLabel("YOL TARİFİ İÇİN\nQR OKUTUNUZ")
        qr_title.setFont(QFont('Geist', 12, QFont.Normal))
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet(f"color: {self.colors['text_secondary']}; background: transparent; padding: 8px;")
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
            border-radius: 12px;
            color: {self.colors['bg_primary']};
            font-size: 16px;
            font-weight: Normal;
        """)
        qr_container_layout.addWidget(self.qr_label)
        qr_container_layout.addStretch()
        
        qr_widget_layout.addWidget(qr_container)
        qr_widget_layout.addStretch()
        content_row_layout.addWidget(qr_widget, 1)
        
        info_layout.addWidget(content_row)
        layout.addWidget(info_container)

    def create_svg_info_display(self, name, phone, address, distance, duration):
        """📱 BİLGİ DISPLAY"""
        # Mevcut widget'ları temizle
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Telefon formatla
        phone = self.format_phone_number(phone)
        
        # ECZANE ADI
        name_label = QLabel(name)
        name_label.setFont(QFont('Geist', 20, QFont.Normal))
        name_label.setStyleSheet(f"color: {self.colors['text_primary']}; padding: 0px;")
        name_label.setWordWrap(True)
        self.info_widget_layout.addWidget(name_label)
        
        # TELEFON
        phone_row = self.create_info_row("icons/phone.svg", "📞", phone, self.colors['accent_blue'])
        self.info_widget_layout.addWidget(phone_row)
        
        # ADRES
        address_row = self.create_info_row("icons/mappin.svg", "📍", address, self.colors['accent_red'], wrap=True)
        self.info_widget_layout.addWidget(address_row)
        
        # MESAFE
        distance_row = self.create_info_row("icons/navigation.svg", "🚗", f"Mesafe: {distance}", self.colors['accent_green'])
        self.info_widget_layout.addWidget(distance_row)
        
        # SÜRE
        time_row = self.create_info_row("icons/clock.svg", "⏱️", f"Süre: {duration}", self.colors['accent_purple'])
        self.info_widget_layout.addWidget(time_row)

    def create_info_row(self, svg_path, fallback_emoji, text, color, wrap=False):
        """Bilgi satırı oluştur"""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setSpacing(12)
        row_layout.setContentsMargins(0, 4, 0, 4)
        if wrap:
            row_layout.setAlignment(Qt.AlignTop)
        
        icon = self.load_svg_icon(svg_path, size=18)
        if icon:
            row_layout.addWidget(icon)
        else:
            fallback = self.create_fallback_icon(fallback_emoji, color, 18)
            row_layout.addWidget(fallback)
        
        label = QLabel(text)
        label.setFont(QFont('Geist', 14))
        label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        if wrap:
            label.setWordWrap(True)
        row_layout.addWidget(label)
        
        if not wrap:
            row_layout.addStretch()
        
        return row

    def create_corporate_qr_map_section(self, layout):
        """🗺️ HARİTA SECTION"""
        self.map_label = QLabel("⏳ Harita yükleniyor...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setFixedHeight(570)
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border-radius: 12px;
            color: {self.colors['text_muted']};
            font-size: 16px;
        """)
        layout.addWidget(self.map_label)
    
        # destination_label hala lazım (on_map_data_ready'de kullanılıyor)
        self.destination_label = QLabel("Nöbetçi Eczane")
        self.destination_label.hide()  # Gizli, sadece veri tutmak için

    def create_corporate_footer(self, layout):
        """🏢 FOOTER"""
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"""
            background: transparent;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 16, 0, 0)
        
        left_text = QLabel("Veriler İzmir Eczacıları Odası'ndan otomatik olarak güncellenmektedir.")
        left_text.setFont(QFont('Geist', 11))
        left_text.setStyleSheet("color: rgba(255, 255, 255, 0.3); background: transparent;")
        footer_layout.addWidget(left_text)
        
        footer_layout.addStretch()
        
        right_text = QLabel("izmireczaciodasi.org.tr")
        right_text.setFont(QFont('Geist', 11))
        right_text.setStyleSheet("color: rgba(255, 255, 255, 0.3); background: transparent;")
        footer_layout.addWidget(right_text)
        
        layout.addWidget(footer)

    def load_logo(self):
        """Logo yükle"""
        try:
            logo_paths = ["logo/LOGO.png", "logo/logo.png", "logo/Logo.png"]
            for path in logo_paths:
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        scaled_logo = pixmap.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_label.setPixmap(scaled_logo)
                        return
            
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Geist', 24))
        except:
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Geist', 24))

    def update_time(self):
        """Saat ve tarih güncelle"""
        now = datetime.now()
        self.time_display.setText(now.strftime("%H:%M:%S"))
        self.date_display.setText(now.strftime("%d.%m.%Y"))

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
        self.no_video_label.setFont(QFont('Geist', 28, QFont.Normal))
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
• AVI (.avi)"""
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
        # Veri güncelleme - 30 dakikada bir
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(1800000)  # 30 dakika

        # Mod kontrolü - dakikada bir
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule_and_switch)
        self.schedule_timer.start(60000)  # 1 dakika
        
        print("⏰ Nöbet saatleri: Hafta içi 18:45-08:45, Cumartesi 16:00-08:45, Pazar tüm gün")

    def setup_animations(self):
        """Animasyon kurulum"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_animation)
        self.pulse_timer.start(1000)
        self.pulse_state = True

    def pulse_animation(self):
        """Pulse efekt"""
        if hasattr(self, 'status_label'):
            if self.pulse_state:
                self.status_label.setStyleSheet(f"""
                    color: {self.colors['accent_green']};
                    background: rgba(48, 209, 88, 0.2);
                    border-radius: 8px;
                    padding: 4px 8px;
                """)
            else:
                self.status_label.setStyleSheet(f"""
                    color: {self.colors['accent_green']};
                    background: transparent;
                """)
            self.pulse_state = not self.pulse_state

    def check_schedule_and_switch(self):
        """
        🕐 NÖBET SAATLERİ KONTROLÜ
        
        Hafta içi (Pazartesi-Cuma): 18:45 - 08:45
        Cumartesi: 16:00 - 08:45 (ertesi gün)
        Pazar: TÜM GÜN
        """
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Pazartesi, 5=Cumartesi, 6=Pazar
        
        # Saatleri tanımla
        time_0845 = datetime.strptime("08:45", "%H:%M").time()
        time_1600 = datetime.strptime("16:00", "%H:%M").time()
        time_1845 = datetime.strptime("18:45", "%H:%M").time()
        
        should_show_pharmacy = False
        
        if current_day == 6:  # PAZAR - TÜM GÜN
            should_show_pharmacy = True
            
        elif current_day == 5:  # CUMARTESİ - 16:00'dan itibaren
            if current_time >= time_1600 or current_time <= time_0845:
                should_show_pharmacy = True
                
        else:  # HAFTA İÇİ (Pazartesi-Cuma) - 18:45'ten itibaren
            if current_time >= time_1845 or current_time <= time_0845:
                should_show_pharmacy = True
        
        # Mod değişimi
        if should_show_pharmacy and self.current_mode != "pharmacy":
            day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            print(f"🏥 NÖBET MODUNA GEÇİYOR - {day_names[current_day]} {now.strftime('%H:%M')}")
            self.switch_to_pharmacy_mode()
            
        elif not should_show_pharmacy and self.current_mode != "video":
            day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            print(f"🎬 REKLAM MODUNA GEÇİYOR - {day_names[current_day]} {now.strftime('%H:%M')}")
            self.switch_to_video_mode()

    def switch_to_video_mode(self):
        """Video moduna geç"""
        self.current_mode = "video"
        self.stacked_widget.setCurrentWidget(self.video_widget)
        
        if self.video_path and os.path.exists(self.video_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.video_path))))
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

    # ========================================================================
    # 🔄 WORKER THREAD İLE VERİ ÇEKME - DONMA YOK!
    # ========================================================================
    
    def fetch_data(self):
        """📡 ECZANE VERİSİ ÇEK - WORKER THREAD"""
        print("📡 Eczane bilgileri güncelleniyor (background)...")
        
        # Loading göster
        self.show_loading_state()
        
        # Worker thread başlat
        self.pharmacy_worker = DataFetchWorker("pharmacy")
        self.pharmacy_worker.pharmacy_data_ready.connect(self.on_pharmacy_data_ready)
        self.pharmacy_worker.error_occurred.connect(self.on_fetch_error)
        self.pharmacy_worker.start()

    def on_pharmacy_data_ready(self, data):
        """✅ Eczane verisi geldi - UI güncelle"""
        if data.get('found'):
            name = data['name']
            if hasattr(self, 'destination_label'):
                    self.destination_label.setText(name)
            phone = data['phone']
            address = data['address']
            maps_url = data['maps_url']
            self.end_lat = data['end_lat']
            self.end_lon = data['end_lon']   
            # Önce mesafe/süre olmadan göster
            self.create_svg_info_display(name, phone, address, "Hesaplanıyor...", "Hesaplanıyor...")
            
            # QR kod oluştur
            if maps_url:
                self.create_qr_code(maps_url)
            
            # Harita için worker başlat
            self.fetch_map_data()   
            
            # Son güncelleme
            now = datetime.now()
            # self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')}")
            
            print(f"✅ Eczane bulundu: {name}")
        else:
            self.show_not_found_state()

    def fetch_map_data(self):
        """🗺️ HARİTA VERİSİ ÇEK - WORKER THREAD"""
        if not self.end_lat or not self.end_lon:
            return
        
        self.map_label.setText("⏳ Harita yükleniyor...")
        
        self.map_worker = DataFetchWorker(
            "map",
            api_key=self.api_key,
            start_lat=self.start_lat,
            start_lon=self.start_lon,
            end_lat=self.end_lat,
            end_lon=self.end_lon
        )
        self.map_worker.map_data_ready.connect(self.on_map_data_ready)
        self.map_worker.error_occurred.connect(self.on_map_error)
        self.map_worker.start()

    def on_map_data_ready(self, data):
        """✅ Harita verisi geldi"""
        try:
            map_bytes = data.get('map_data')
            if map_bytes:
                pixmap = QPixmap()
                pixmap.loadFromData(map_bytes)
                scaled_pixmap = pixmap.scaled(820, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # Overlay'i pixmap üzerine çiz
                from PyQt5.QtGui import QPainter, QLinearGradient, QPen
                
                painter = QPainter(scaled_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Gradient overlay
                gradient = QLinearGradient(0, scaled_pixmap.height() - 60, 0, scaled_pixmap.height())
                gradient.setColorAt(0, QColor(0, 0, 0, 0))
                gradient.setColorAt(0.5, QColor(0, 0, 0, 180))
                gradient.setColorAt(1, QColor(0, 0, 0, 240))
                
                painter.fillRect(0, scaled_pixmap.height() - 60, scaled_pixmap.width(), 60, gradient)
                
                # Yazıları çiz
                painter.setPen(QColor(255, 255, 255, 100))
                painter.setFont(QFont('Geist', 8))
                painter.drawText(50, scaled_pixmap.height() - 38, "ROTA")
                
                painter.setPen(QColor(255, 255, 255, 150))
                painter.setFont(QFont('Geist', 11))
                painter.drawText(50, scaled_pixmap.height() - 18, f"Eczaneniz → {self.destination_label.text()}")
                
                # İkon kutusu
                painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
                painter.drawRoundedRect(10, scaled_pixmap.height() - 48, 32, 32, 4, 4)
                
                painter.setPen(QColor(255, 255, 255, 255))
                painter.setFont(QFont('Geist', 14))
                painter.drawText(18, scaled_pixmap.height() - 24, "↗")
                
                painter.end()
                
                self.map_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            print(f"❌ Harita gösterme hatası: {e}")
            self.map_label.setText("❌ Harita yüklenemedi")

    def update_distance_duration(self, distance, duration):
        """Mesafe ve süre bilgisini güncelle"""
        # Info widget'taki label'ları bul ve güncelle
        for i in range(self.info_widget_layout.count()):
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                # QHBoxLayout içindeki QLabel'ları bul
                layout = widget.layout()
                if layout:
                    for j in range(layout.count()):
                        item = layout.itemAt(j)
                        if item and item.widget():
                            label = item.widget()
                            if isinstance(label, QLabel):
                                text = label.text()
                                if "Mesafe:" in text:
                                    label.setText(f"Mesafe: {distance}")
                                elif "Süre:" in text:
                                    label.setText(f"Süre: {duration}")

    def on_map_error(self, error_msg):
        """Harita hatası"""
        print(f"❌ {error_msg}")
        self.map_label.setText("❌ Harita yüklenemedi")
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            color: {self.colors['text_secondary']};
            font-size: 16px;
            border-radius: 12px;
        """)

    def fetch_weather_data(self):
        """🌤️ HAVA DURUMU ÇEK - WORKER THREAD"""
        print("🌡️ Hava durumu alınıyor (background)...")
        
        self.weather_worker = DataFetchWorker(
            "weather",
            api_key=self.weather_api_key
        )
        self.weather_worker.weather_data_ready.connect(self.on_weather_data_ready)
        self.weather_worker.error_occurred.connect(self.on_weather_error)
        self.weather_worker.start()

    def on_weather_data_ready(self, data):
        """✅ Hava durumu geldi"""
        temp = data['temp']
        weather_main = data['weather_main']
        
        # Lottie animasyonu dene
        lottie_loaded = self.load_lottie_animation(weather_main, temp)
        
        if lottie_loaded:
            self.weather_icon.hide()
            self.lottie_widget.show()
        else:
            self.lottie_widget.hide()
            self.weather_icon.show()
            self.weather_icon.setText(self.get_weather_emoji(weather_main, temp))
        
        self.weather_temp.setText(f"{temp}°C")
        print(f"✅ Hava durumu: {temp}°C - {weather_main}")

    def on_weather_error(self, error_msg):
        """Hava durumu hatası"""
        print(f"❌ {error_msg}")
        self.weather_temp.setText("--°C")
        self.weather_icon.setText("❓")
        self.weather_icon.show()
        self.lottie_widget.hide()

    def on_fetch_error(self, error_msg):
        """Genel fetch hatası"""
        print(f"❌ {error_msg}")
        self.show_error_state(error_msg)

    def show_loading_state(self):
        """Loading durumu göster"""
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        loading_label = QLabel("⏳ Nöbetçi eczane bilgileri yükleniyor...")
        loading_label.setFont(QFont('Geist', 16))
        loading_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        loading_label.setAlignment(Qt.AlignCenter)
        self.info_widget_layout.addWidget(loading_label)

    def show_not_found_state(self):
        """Bulunamadı durumu"""
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        error_label = QLabel("❌ KARŞIYAKA 4'te nöbetçi eczane bulunamadı")
        error_label.setFont(QFont('Geist', 16))
        error_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        error_label.setAlignment(Qt.AlignCenter)
        self.info_widget_layout.addWidget(error_label)
        
        now = datetime.now()
        self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")

    def show_error_state(self, error_msg):
        """Hata durumu"""
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        error_label = QLabel(f"❌ Bağlantı hatası:\n{error_msg}")
        error_label.setFont(QFont('Geist', 14))
        error_label.setStyleSheet(f"color: {self.colors['accent_red']};")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        self.info_widget_layout.addWidget(error_label)
        
        now = datetime.now()
        self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Hata)")

    def format_phone_number(self, phone):
        """📞 Telefon formatla: 0232 999 99 99"""
        try:
            digits = ''.join(filter(str.isdigit, phone))
            
            if len(digits) == 11 and digits.startswith('0'):
                return f"{digits[:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"
            elif len(digits) == 10:
                digits = '0' + digits
                return f"{digits[:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"
            else:
                return phone
        except:
            return phone

    def get_weather_emoji(self, weather_main, temp):
        """Weather emoji"""
        if weather_main in ['clear', 'sunny']:
            return "🔥" if temp >= 30 else ("☀" if temp >= 25 else "🌤")
        elif weather_main in ['clouds']:
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
            
        except Exception as e:
            self.qr_label.setText("QR\nHatası")
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
        elif event.key() == Qt.Key_R:
            # Manuel yenileme
            print("🔄 Manuel yenileme...")
            self.fetch_data()
            self.fetch_weather_data()

    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        # Worker thread'leri durdur
        if self.pharmacy_worker and self.pharmacy_worker.isRunning():
            self.pharmacy_worker.terminate()
        if self.weather_worker and self.weather_worker.isRunning():
            self.weather_worker.terminate()
        if self.map_worker and self.map_worker.isRunning():
            self.map_worker.terminate()
        
        event.accept()


# ============================================================================
# 🚀 MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🏥 KARŞIYAKA 4 NÖBETÇİ ECZANE SİSTEMİ")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    font = QFont("Geist", 12)
    app.setFont(font)
    
    try:
        window = ModernCorporateEczaneApp()
        
        print("\n📊 Sistem Durumu:")
        print("   ✅ Worker Thread - UI donması önlendi")
        print("   ✅ Cumartesi 16:00 nöbet desteği")
        print("   ✅ HTTP Server + Lottie")
        print("   ✅ SVG ikonlar + QR kod + Harita")
        print("\n⌨️  Kısayollar:")
        print("   ESC  : Çıkış")
        print("   F11  : Tam ekran")
        print("   R    : Manuel yenileme")
        print("\n🕐 Nöbet Saatleri:")
        print("   Pazartesi-Cuma : 18:45 - 08:45")
        print("   Cumartesi      : 16:00 - 08:45")
        print("   Pazar          : Tüm gün")
        print("=" * 70)
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()