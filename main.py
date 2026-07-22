import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from dotenv import load_dotenv
load_dotenv()
import http.server
import socketserver
import sys
import os
import requests
from bs4 import BeautifulSoup
from PyQt5.QtGui import QPainterPath
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
import threading
from config import Config


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
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            h4_elements = soup.find_all('h4', class_='red')
            
            for h4 in h4_elements:
                strong = h4.find('strong')
                if strong and Config.TARGET_REGION in strong.text.upper():
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
                    end_lat, end_lon = Config.DEFAULT_END_LAT, Config.DEFAULT_END_LON
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
            # Hata olursa boş sinyal gönder (UI son veriyi korur)
            print(f"⚠️ Site erişilemedi: {e}")
            self.pharmacy_data_ready.emit({'found': False, 'keep_current': True})
    
    def fetch_weather_data(self):
        """🌤️ Hava durumu çek"""
        try:
            api_key = self.kwargs.get('api_key')
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': Config.CITY_NAME + ",TR",
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
            directions_response.raise_for_status()
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

                map_width = Config.MAP_WIDTH
                map_height = Config.MAP_HEIGHT

                lat_diff = abs(end_lat - start_lat)
                lon_diff = abs(end_lon - start_lon)
                padding_factor = 0.25
                lat_pad = max(lat_diff * padding_factor, 0.002)
                lon_pad = max(lon_diff * padding_factor, 0.002)

                min_lat = min(start_lat, end_lat) - lat_pad
                max_lat = max(start_lat, end_lat) + lat_pad
                min_lon = min(start_lon, end_lon) - lon_pad
                max_lon = max(start_lon, end_lon) + lon_pad

                static_map_url = (
                    f"https://maps.googleapis.com/maps/api/staticmap?"
                    f"size={map_width}x{map_height}&"
                    f"maptype=roadmap&"
                    f"visible={min_lat},{min_lon}|{max_lat},{max_lon}&"
                    f"markers=color:blue|size:mid|label:B|{start_lat},{start_lon}&"
                    f"markers=color:red|size:mid|label:E|{end_lat},{end_lon}&"
                    f"path=color:0x007AFF|weight:5|enc:{polyline}&"
                    f"scale=2&"
                    f"key={api_key}"
                )

                map_response = requests.get(static_map_url, timeout=15)
                map_response.raise_for_status()
                ct = map_response.headers.get("Content-Type", "")
                if not ct.startswith("image/"):
                    self.error_occurred.emit("Harita görseli çözümlenemedi")
                    return
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


class RoundedCoverMapLabel(QLabel):
    """Map image label that draws in cover mode while preserving aspect ratio."""

    def __init__(self, *args, corner_radius=12, **kwargs):
        super().__init__(*args, **kwargs)
        self._map_pixmap = None
        self._corner_radius = corner_radius
        self._rota_text = None
        self._info_text = None

    def set_map_pixmap(self, pixmap):
        self._map_pixmap = pixmap
        self.update()

    def clear_map_pixmap(self):
        self._map_pixmap = None
        self.update()

    def set_overlay_text(self, rota_text, info_text):
        self._rota_text = rota_text
        self._info_text = info_text
        self.update()

    def paintEvent(self, event):
        if not self._map_pixmap or self._map_pixmap.isNull():
            super().paintEvent(event)
            return

        from PyQt5.QtGui import QLinearGradient
        from PyQt5.QtCore import QRect

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        painter.setClipPath(path)

        scaled = self._map_pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation,
        )
        x = (scaled.width() - self.width()) // 2
        y = (scaled.height() - self.height()) // 2
        painter.drawPixmap(-x, -y, scaled)

        gradient_height = 60
        gradient = QLinearGradient(0, self.height() - gradient_height, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.5, QColor(0, 0, 0, 180))
        gradient.setColorAt(1, QColor(0, 0, 0, 240))
        painter.fillRect(0, self.height() - gradient_height, self.width(), gradient_height, gradient)

        if hasattr(self, '_rota_text') and self._rota_text:
            painter.setPen(QColor(255, 255, 255, 100))
            painter.setFont(QFont('Plus Jakarta Sans', 8))
            painter.drawText(20, self.height() - 38, "ROTA")

            painter.setPen(QColor(255, 255, 255, 220))
            painter.setFont(QFont('Plus Jakarta Sans', 13))
            painter.drawText(20, self.height() - 16, self._rota_text)

        if hasattr(self, '_info_text') and self._info_text:
            painter.setPen(QColor(255, 255, 255, 180))
            painter.setFont(QFont('Plus Jakarta Sans', 11))
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(self._info_text)
            painter.drawText(self.width() - text_width - 20, self.height() - 16, self._info_text)


class RoundedPreviewLabel(QLabel):
    """Label that clips its pixmap to rounded corners, like RoundedCoverMapLabel but without the overlay text."""

    def __init__(self, *args, corner_radius=12, **kwargs):
        super().__init__(*args, **kwargs)
        self._corner_radius = corner_radius

    def paintEvent(self, event):
        pixmap = self.pixmap()
        if not pixmap or pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)


# ============================================================================
# 🏥 ANA UYGULAMA
# ============================================================================
class ModernCorporateEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Config.TARGET_REGION} Nöbetçi Eczane")

        # 🌐 LOCAL HTTP SERVER BAŞLAT
        self.start_local_server()
        
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.weather_api_key = Config.OPENWEATHER_API_KEY
        if not self.api_key:
            print("Uyari: GOOGLE_MAPS_KEY veya GOOGLE_MAPS_API_KEY tanimli degil.")
        if not self.weather_api_key:
            print("Uyari: OPENWEATHER_KEY veya OPENWEATHER_API_KEY tanimli degil.")

        self.start_lat = Config.START_LAT
        self.start_lon = Config.START_LON
        
        # Eczane koordinatları (güncellenecek)
        self.end_lat = None
        self.end_lon = None
        
        self.current_mode = None
        self.video_path = None
        self.video_files = []
        self.image_files = []
        self.current_slide_index = 0
        self.current_video_index = 0
        self.slide_timer = None
        self.card_row_horizontal_margin = 24  # matches red header's content margins (see create_red_header_with_lottie)

        # 🖼️ Alt reklam önizleme slaytı
        self.ad_preview_images = []
        self.ad_preview_index = 0
        self.ad_preview_timer = None
        
        # Worker thread referansları
        self.pharmacy_worker = None
        self.weather_worker = None
        self.map_worker = None

        # İlk başarılı gösterimden sonra refresh sırasında ekran silinmesin
        self.has_displayed_pharmacy_data = False
        self.has_displayed_map = False

        # 🔁 Fetch hatasında 60 saniyede bir yeniden dene (2 saatlik timer'ı bekleme)
        self.retry_timer = QTimer()
        self.retry_timer.setSingleShot(True)
        self.retry_timer.timeout.connect(self.retry_failed_fetches)
        
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

    def setup_lottie_weather(self, parent):
        """🎬 LOTTIE SİSTEMİ"""
        # Keep the underlying Qt/GLib object owned until it is reparented into
        # the weather row's layout.
        self.lottie_widget = QWebEngineView(parent)
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
        label.setFont(QFont('Plus Jakarta Sans', size-4))
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
                font-family: 'Plus Jakarta Sans', 'Helvetica Neue', sans-serif;
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
        layout.setContentsMargins(40, 32, 40, 0)

        self.setup_lottie_weather(content_widget)
        self.create_red_header_with_lottie(layout)
        self.create_svg_info_section(layout)
        self.create_corporate_qr_map_section(layout)
        self.create_ad_preview_section(layout)
        self.create_corporate_footer(layout)

        # Harita için kalan yüksekliği hesapla (ad_preview artık sabit 380px, görseller esnemiyor)
        screen_height = QApplication.desktop().screenGeometry().height()
        header_height = 140
        info_card_height = 400  # başlık dahil, kart tek parça sabit yükseklikte
        ad_preview_height = 380
        footer_height = 50
        vertical_margins = 32 + 0  # layout.setContentsMargins üst/alt
        spacing_gaps = 24 * 4  # header, info, map, ad, footer arasındaki 4 boşluk
        used_height = header_height + info_card_height + ad_preview_height + footer_height + vertical_margins + spacing_gaps
        map_remaining_height = max(screen_height - used_height, 150)
        self.map_label.setFixedHeight(map_remaining_height)

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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B71C1C, stop:0.5 #C62828, stop:1 #B71C1C);
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
        main_title.setFont(QFont('Plus Jakarta Sans', 26, QFont.Normal))
        main_title.setStyleSheet("color: white; background: transparent;")
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("Nöbetçi Eczane Sistemi")
        sub_title.setFont(QFont('Plus Jakarta Sans', 13, QFont.Normal))
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
        self.time_display.setFont(QFont('Plus Jakarta Sans', 18, QFont.Normal))
        self.time_display.setStyleSheet("color: white; background: transparent;")
        datetime_row_layout.addWidget(self.time_display)
        
        bullet = QLabel("•")
        bullet.setFont(QFont('Plus Jakarta Sans', 18, QFont.Normal))
        bullet.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent; padding-bottom: 1px;")
        datetime_row_layout.addWidget(bullet)
        
        self.date_display = QLabel()
        self.date_display.setFont(QFont('Plus Jakarta Sans', 18, QFont.Normal))
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
        self.weather_temp.setFont(QFont('Plus Jakarta Sans', 16, QFont.Normal))
        self.weather_temp.setStyleSheet("color: white; background: transparent; none;")
        weather_row_layout.addWidget(self.weather_temp)
        
        self.weather_icon = QLabel("☀")
        self.weather_icon.setFont(QFont('Plus Jakarta Sans', 16))
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
        info_layout.setContentsMargins(self.card_row_horizontal_margin, 24, self.card_row_horizontal_margin, 24)
        info_layout.setSpacing(20)
        
        title = QLabel("NÖBETÇİ ECZANE BİLGİLERİ")
        title.setFont(QFont('Plus Jakarta Sans', 20, QFont.Normal))
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
        loading_label.setFont(QFont('Plus Jakarta Sans', 16))
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
        qr_title.setFont(QFont('Plus Jakarta Sans', 12, QFont.Normal))
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
        self.qr_label.setFixedSize(Config.QR_SIZE, Config.QR_SIZE)
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

    def create_svg_info_display(self, name, phone, address):
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
        name_label.setFont(QFont('Plus Jakarta Sans', 20, QFont.Normal))
        name_label.setStyleSheet(f"color: {self.colors['text_primary']}; padding: 0px;")
        name_label.setWordWrap(True)
        self.info_widget_layout.addWidget(name_label)
        
        # TELEFON
        rows_container = QWidget()
        rows_container.setStyleSheet("background: transparent;")
        rows_layout = QVBoxLayout(rows_container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(18)

        phone_row, _ = self.create_info_row("icons/phone.svg", "📞", phone, self.colors['accent_blue'])
        rows_layout.addWidget(phone_row)

        # ADRES
        address_row, _ = self.create_info_row("icons/mappin.svg", "📍", address, self.colors['accent_red'], wrap=True)
        rows_layout.addWidget(address_row)

        # MESAFE
        distance_row, self._distance_row_label = self.create_info_row("icons/navigation.svg", "🚗", "Mesafe: Hesaplanıyor...", self.colors['accent_green'])
        rows_layout.addWidget(distance_row)

        self.info_widget_layout.addWidget(rows_container)

    def create_info_row(self, svg_path, fallback_emoji, text, color, wrap=False):
        """Bilgi satırı oluştur"""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setSpacing(12)
        # Every info row uses the same vertical margin; inter-row spacing is
        # controlled by rows_layout in create_svg_info_display.
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
        label.setFont(QFont('Plus Jakarta Sans', 14))
        label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        if wrap:
            label.setWordWrap(True)
        row_layout.addWidget(label)
        
        if not wrap:
            row_layout.addStretch()

        return row, label

    def create_corporate_qr_map_section(self, layout):
        """🗺️ HARİTA SECTION"""
        map_row = QWidget()
        map_row.setStyleSheet("background: transparent;")
        map_row_layout = QHBoxLayout(map_row)
        map_row_layout.setContentsMargins(self.card_row_horizontal_margin, 0, self.card_row_horizontal_margin, 0)

        self.map_label = RoundedCoverMapLabel("Harita yukleniyor...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setFixedHeight(Config.MAP_HEIGHT)
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border-radius: 12px;
            color: {self.colors['text_muted']};
            font-size: 16px;
        """)

        map_row_layout.addWidget(self.map_label)
        layout.addWidget(map_row)

        # destination_label hala lazım (on_map_data_ready'de kullanılıyor)
        self.destination_label = QLabel("Nöbetçi Eczane")
        self.destination_label.hide()  # Gizli, sadece veri tutmak için

    def create_ad_preview_section(self, layout):
        """🖼️ Haritanın altında reklam görsellerinin alt kısmını gösteren slayt"""
        ad_row = QWidget()
        ad_row.setStyleSheet("background: transparent;")
        ad_row_layout = QHBoxLayout(ad_row)
        ad_row_layout.setContentsMargins(self.card_row_horizontal_margin, 0, self.card_row_horizontal_margin, 0)

        self.ad_preview_label = RoundedPreviewLabel()
        self.ad_preview_label.setAlignment(Qt.AlignCenter)
        self.ad_preview_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border-radius: 12px;
        """)

        # PNG görseller 900x380, oranı bozmamak için sabit yükseklik
        self.ad_preview_label.setFixedHeight(380)
        ad_row_layout.addWidget(self.ad_preview_label)
        layout.addWidget(ad_row)

        self.load_ad_preview_images()

    def load_ad_preview_images(self):
        """ads_preview/ klasöründeki görselleri alfabetik sırayla yükle"""
        ads_dir = "ads_preview"
        self.ad_preview_images = []

        if not os.path.exists(ads_dir):
            return

        try:
            for file in sorted(os.listdir(ads_dir)):
                if file.lower().endswith(('.png', '.jpg')):
                    self.ad_preview_images.append(os.path.join(ads_dir, file))
        except OSError:
            return

    def show_next_ad_preview(self):
        """🖼️ Sıradaki reklam görselinin alt kısmını göster"""
        if not self.ad_preview_images:
            return

        idx = self.ad_preview_index % len(self.ad_preview_images)
        image_path = self.ad_preview_images[idx]

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.ad_preview_label.width(),
                380,
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            self.ad_preview_label.setPixmap(scaled)

        self.ad_preview_index += 1

    def create_corporate_footer(self, layout):
        """🏢 FOOTER"""
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"""
            background: transparent;
            border: none;
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 16, 0, 0)
        
        left_text = QLabel("Veriler İzmir Eczacıları Odası'ndan otomatik olarak güncellenmektedir.")
        left_text.setFont(QFont('Plus Jakarta Sans', 11))
        left_text.setStyleSheet("color: rgba(255, 255, 255, 0.3); background: transparent;")
        footer_layout.addWidget(left_text)
        
        footer_layout.addStretch()
        
        right_text = QLabel("izmireczaciodasi.org.tr")
        right_text.setFont(QFont('Plus Jakarta Sans', 11))
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
            self.logo_label.setFont(QFont('Plus Jakarta Sans', 24))
        except:
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Plus Jakarta Sans', 24))

    def update_time(self):
        """Saat ve tarih güncelle"""
        now = datetime.now()
        self.time_display.setText(now.strftime("%H:%M"))
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
        self.no_video_label.setFont(QFont('Plus Jakarta Sans', 28, QFont.Normal))
        self.no_video_label.setStyleSheet(f"""
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
            padding: 50px;
        """)
        self.update_video_message()
        layout.addWidget(self.no_video_label)

        # Overlay label for image slideshow — covers the full video widget
        self.slide_label = QLabel(widget)
        self.slide_label.setGeometry(0, 0, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.slide_label.setAlignment(Qt.AlignCenter)
        self.slide_label.setStyleSheet("background-color: #000000;")
        self.slide_label.hide()

    def update_video_message(self):
        """Video mesajını güncelle"""
        if not self.video_path and not getattr(self, 'image_files', []):
            message = """📺 REKLAM MODU

ads/ klasöründe dosya bulunamadı.

Desteklenen formatlar:
• MP4 (.mp4)
• MOV (.mov)
• AVI (.avi)
• PNG (.png)
• JPG (.jpg)"""
        else:
            message = "🎬 Yükleniyor..."

        self.no_video_label.setText(message)

    def setup_video_player(self):
        """Video player kurulum"""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget_display)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.check_ad_files()

    def check_ad_files(self):
        """ads/ klasöründeki video ve görsel dosyalarını tara"""
        ads_dir = "ads"
        self.video_files = []
        self.image_files = []
        self.video_path = None

        if not os.path.exists(ads_dir):
            return

        try:
            for file in sorted(os.listdir(ads_dir)):
                path = os.path.join(ads_dir, file)
                lower = file.lower()
                if lower.endswith(('.mp4', '.mov', '.avi')):
                    self.video_files.append(path)
                elif lower.endswith(('.png', '.jpg', '.jpeg')):
                    self.image_files.append(path)
        except OSError:
            return

        if self.video_files:
            self.video_path = self.video_files[0]
            print(f"✅ {len(self.video_files)} video bulundu")
        if self.image_files:
            print(f"✅ {len(self.image_files)} görsel bulundu")

    def on_media_status_changed(self, status):
        """Video status değişimi"""
        if status in (QMediaPlayer.EndOfMedia, QMediaPlayer.InvalidMedia):
            self.current_video_index += 1
            if self.current_video_index < len(self.video_files):
                self._play_current_video()
            elif self.image_files:
                # Tüm videolar bitti, slayta dön
                self.current_slide_index = 0
                self.show_next_slide()
            else:
                # Sadece video var, başa dön
                self.current_video_index = 0
                self._play_current_video()

    def show_next_slide(self):
        """Slayt gösterisi: mevcut görseli göster, 15 sn sonra bir sonrakine geç"""
        if self.current_mode != 'video' or not self.image_files:
            return

        idx = self.current_slide_index % len(self.image_files)
        path = self.image_files[idx]

        pixmap = QPixmap(path)
        if not pixmap.isNull():
            w, h = Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT
            scaled = pixmap.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - w) // 2
            y = (scaled.height() - h) // 2
            self.slide_label.setPixmap(scaled.copy(x, y, w, h))
            self.slide_label.setText("")
            self.slide_label.setStyleSheet("background-color: #000000;")
        else:
            self.slide_label.setPixmap(QPixmap())
            self.slide_label.setText("⚠ Görsel yüklenemedi")
            self.slide_label.setStyleSheet("background-color: #000000; color: #ffffff; font-size: 18px;")

        self.slide_label.show()
        self.slide_label.raise_()
        self.video_widget_display.hide()
        self.no_video_label.hide()

        self.current_slide_index += 1
        if self.current_slide_index >= len(self.image_files) and self.video_files:
            self.slide_timer = None
            self._start_video_playlist()
            return

        if self.slide_timer is not None:
            self.slide_timer.stop()

        self.slide_timer = QTimer()
        self.slide_timer.setSingleShot(True)
        self.slide_timer.timeout.connect(self.show_next_slide)
        self.slide_timer.start(Config.SLIDE_DURATION)

    def _start_video_playlist(self):
        """Tüm görseller gösterildikten sonra video listesini başlat"""
        if self.current_mode != 'video' or not self.video_files:
            return
        self.current_video_index = 0
        self._play_current_video()

    def _play_current_video(self):
        """video_files listesindeki mevcut videoyu oynat"""
        if self.current_mode != 'video' or not self.video_files:
            return
        path = self.video_files[self.current_video_index % len(self.video_files)]
        if os.path.exists(path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(path))))
            self.media_player.play()
            self.slide_label.hide()
            self.no_video_label.hide()
            self.video_widget_display.show()
            print(f"▶️ Video oynatılıyor: {path}")

    def setup_timers(self):
        """Timer kurulum"""
        # Veri güncelleme
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(Config.PHARMACY_UPDATE_INTERVAL)

        # Hava durumu güncelleme
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.fetch_weather_data)
        self.weather_timer.start(Config.WEATHER_UPDATE_INTERVAL)

        # Mod kontrolü
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule_and_switch)
        self.schedule_timer.start(Config.MODE_CHECK_INTERVAL)

        # Alt reklam önizleme slaytı
        self.ad_preview_timer = QTimer()
        self.ad_preview_timer.timeout.connect(self.show_next_ad_preview)

        print("⏰ Nöbet saatleri: Hafta içi 18:45-08:45, Cumartesi 16:00-08:55, Pazar tüm gün")

    def check_schedule_and_switch(self):
        if Config.is_ad_mode():
            if self.current_mode != 'video':
                self.switch_to_video_mode()
        else:
            if self.current_mode != 'pharmacy':
                self.switch_to_pharmacy_mode()

    def switch_to_video_mode(self):
        """Video/slayt moduna geç"""
        self.current_mode = "video"
        self.stacked_widget.setCurrentWidget(self.video_widget)

        if self.ad_preview_timer is not None:
            self.ad_preview_timer.stop()

        if self.image_files:
            self.current_slide_index = 0
            self.show_next_slide()
            print(f"🖼️ Slayt gösterisi başlatıldı: {len(self.image_files)} görsel")
        elif self.video_files:
            self.current_video_index = 0
            self._play_current_video()
        else:
            self.slide_label.hide()
            self.video_widget_display.hide()
            self.no_video_label.show()
            print("❌ Reklam dosyası bulunamadı")

    def switch_to_pharmacy_mode(self):
        """Eczane moduna geç"""
        self.current_mode = "pharmacy"

        if self.slide_timer is not None:
            self.slide_timer.stop()
            self.slide_timer = None

        if hasattr(self, 'media_player') and self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()

        self.stacked_widget.setCurrentWidget(self.pharmacy_widget)
        self.fetch_data()
        self.fetch_weather_data()

        if self.ad_preview_timer is not None:
            QTimer.singleShot(200, self.show_next_ad_preview)
            self.ad_preview_timer.start(15000)

    # ========================================================================
    # 🔄 WORKER THREAD İLE VERİ ÇEKME - DONMA YOK!
    # ========================================================================
    
    def retry_failed_fetches(self):
        """🔁 Bağlantı hatası sonrası her şeyi yeniden dene"""
        print("🔁 Bağlantı hatası sonrası yeniden deneniyor...")
        self.fetch_data()
        self.fetch_weather_data()

    def fetch_data(self):
        """📡 ECZANE VERİSİ ÇEK - WORKER THREAD"""
        print("📡 Eczane bilgileri güncelleniyor (background)...")

        # Loading sadece ilk açılışta göster; refresh'te mevcut bilgi ekranda kalsın
        if not self.has_displayed_pharmacy_data:
            self.show_loading_state()
        
        # Worker thread başlat
        self.pharmacy_worker = DataFetchWorker("pharmacy")
        self.pharmacy_worker.pharmacy_data_ready.connect(self.on_pharmacy_data_ready)
        self.pharmacy_worker.error_occurred.connect(self.on_fetch_error)
        self.pharmacy_worker.start()

    def on_pharmacy_data_ready(self, data):
        """✅ Eczane verisi geldi - UI güncelle"""
        if data.get('keep_current'):
            print("⚠️ Site erişilemedi, mevcut veri korunuyor")
            self.retry_timer.start(Config.RETRY_INTERVAL)
            return
        if data.get('found'):
            self.retry_timer.stop()
            name = data['name']
            if hasattr(self, 'destination_label'):
                    self.destination_label.setText(name)
            phone = data['phone']
            address = data['address']
            maps_url = data['maps_url']
            self.end_lat = data['end_lat']
            self.end_lon = data['end_lon']   
            # Önce mesafe/süre olmadan göster
            self.create_svg_info_display(name, phone, address)
            self.has_displayed_pharmacy_data = True

            # QR kod oluştur
            if maps_url:
                self.create_qr_code(maps_url)

            # Harita için worker başlat
            self.fetch_map_data()

            print(f"✅ Eczane bulundu: {name}")
        else:
            self.show_not_found_state()

    def fetch_map_data(self):
        """🗺️ HARİTA VERİSİ ÇEK - WORKER THREAD"""
        if self.end_lat is None or self.end_lon is None:
            return
        
        # Loading sadece hiç harita gösterilmemişse; refresh'te eski harita kalsın
        if not self.has_displayed_map:
            self.map_label.clear_map_pixmap()
            self.map_label.setText("Harita yukleniyor...")

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
                if not pixmap.loadFromData(map_bytes):
                    self.retry_timer.start(Config.RETRY_INTERVAL)
                    # Eski harita ekrandaysa koru, sadece hiç harita yoksa hata göster
                    if not self.has_displayed_map:
                        self.map_label.setText("❌ Harita yüklenemedi")
                    return
                distance = data.get('distance', '~2 km')
                duration = data.get('duration', '~5 dakika')

                self.update_distance_duration(distance, duration)
                self.map_label.setText("")
                self.map_label.set_map_pixmap(pixmap)
                self.has_displayed_map = True
                self.retry_timer.stop()

        except Exception as e:
            print(f"❌ Harita gösterme hatası: {e}")
            self.retry_timer.start(Config.RETRY_INTERVAL)
            if not self.has_displayed_map:
                self.map_label.clear_map_pixmap()
                self.map_label.setText("❌ Harita yüklenemedi")

    def update_distance_duration(self, distance, duration):
        if hasattr(self, '_distance_row_label') and self._distance_row_label:
            self._distance_row_label.setText(f"Mesafe: {distance}  ({duration})")
        pharmacy_name = self.destination_label.text() if hasattr(self, 'destination_label') else "Nöbetçi Eczane"
        self.map_label.set_overlay_text(
            f"Eczaneniz  →  {pharmacy_name}",
            f"{distance}  •  {duration}"
        )

    def on_map_error(self, error_msg):
        """Harita hatası"""
        print(f"❌ {error_msg}")
        self.retry_timer.start(Config.RETRY_INTERVAL)
        if self.has_displayed_map:
            # Eski harita ekranda kalsın
            return
        self.map_label.clear_map_pixmap()
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
        self.retry_timer.start(Config.RETRY_INTERVAL)
        # Ekranda geçerli veri varsa silme, mevcut bilgi kalsın
        if not self.has_displayed_pharmacy_data:
            self.show_error_state(error_msg)

    def show_loading_state(self):
        """Loading durumu göster"""
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        loading_label = QLabel("⏳ Nöbetçi eczane bilgileri yükleniyor...")
        loading_label.setFont(QFont('Plus Jakarta Sans', 16))
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
        error_label.setFont(QFont('Plus Jakarta Sans', 16))
        error_label.setStyleSheet(f"color: {self.colors['text_secondary']};")
        error_label.setAlignment(Qt.AlignCenter)
        self.info_widget_layout.addWidget(error_label)

    def show_error_state(self, error_msg):
        """Hata durumu"""
        for i in reversed(range(self.info_widget_layout.count())): 
            widget = self.info_widget_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        error_label = QLabel(f"❌ Bağlantı hatası:\n{error_msg}")
        error_label.setFont(QFont('Plus Jakarta Sans', 14))
        error_label.setStyleSheet(f"color: {self.colors['accent_red']};")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        self.info_widget_layout.addWidget(error_label)

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
            
            scaled_pixmap = pixmap.scaled(Config.QR_SIZE, Config.QR_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            rounded_pixmap = QPixmap(scaled_pixmap.size())
            rounded_pixmap.fill(Qt.transparent)

            painter = QPainter(rounded_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, scaled_pixmap.width(), scaled_pixmap.height(), 12, 12)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()

            self.qr_label.setPixmap(rounded_pixmap)
            
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
def main():
    os.environ['G_MESSAGES_DEBUG'] = ''
    warnings.filterwarnings('ignore')

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import urllib.request
    import zipfile

    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, 'PlusJakartaSans.ttf')

    if not os.path.exists(font_path):
        url = "https://github.com/tokotype/PlusJakartaSans/raw/master/fonts/ttf/PlusJakartaSans-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)

    app = QApplication(sys.argv)

    from PyQt5.QtGui import QFontDatabase
    QFontDatabase.addApplicationFont(font_path)
    window = ModernCorporateEczaneApp()
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
