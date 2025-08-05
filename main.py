import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QScrollArea, QSizePolicy, QFrame, QGraphicsDropShadowEffect,
                             QStackedLayout)
from PyQt5.QtGui import (QPixmap, QPainter, QPainterPath, QColor, QFont,
                          QLinearGradient, QRadialGradient, QBrush, QPen)
from PyQt5.QtCore import Qt, QUrl, QTimer, QTime, QSize, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import os
import re
import time
from io import BytesIO
from urllib.parse import quote_plus

try:
    from PIL import Image
    import qrcode
except ImportError:
    print("PIL ve qrcode kütüphaneleri gerekli:")
    print("pip install Pillow qrcode")

# --- API Configuration ---
API_CONFIG = {
    'google_maps': "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE",
    'openweather': "b0d1be7721b4967d8feb810424bd9b6f",
    'city': "İzmir",
    'target_region': "KARŞIYAKA 4"
}

# --- Modern Animated Widget Base ---
class AnimatedWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def fade_in(self, duration=1000):
        self.fade_animation.setDuration(duration)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

# --- Glassmorphism Logo Component ---
class GlassmorphismLogo(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Outer glassmorphism ring
        outer_gradient = QRadialGradient(60, 60, 60)
        outer_gradient.setColorAt(0, QColor(255, 255, 255, 80))
        outer_gradient.setColorAt(0.7, QColor(255, 255, 255, 40))
        outer_gradient.setColorAt(1, QColor(255, 255, 255, 10))
        
        painter.setBrush(QBrush(outer_gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 100), 3))
        painter.drawEllipse(5, 5, 110, 110)
        
        # Inner glow circle
        inner_gradient = QRadialGradient(60, 60, 45)
        inner_gradient.setColorAt(0, QColor(102, 126, 234, 60))
        inner_gradient.setColorAt(0.5, QColor(118, 75, 162, 40))
        inner_gradient.setColorAt(1, QColor(240, 147, 251, 20))
        
        painter.setBrush(QBrush(inner_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(20, 20, 80, 80)
        
        # Logo content area
        if self.pixmap():
            pix = self.pixmap()
            scaled_pix = pix.scaled(70, 70, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            path = QPainterPath()
            path.addEllipse(QRectF(25, 25, 70, 70))
            painter.setClipPath(path)
            
            x = (120 - scaled_pix.width()) / 2
            y = (120 - scaled_pix.height()) / 2
            painter.drawPixmap(int(x), int(y), scaled_pix)
        else:
            # Default pharmacy cross icon
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(Qt.NoPen)
            # Vertical bar
            painter.drawRoundedRect(55, 35, 10, 50, 5, 5)
            # Horizontal bar
            painter.drawRoundedRect(35, 55, 50, 10, 5, 5)

# --- Modern Weather Widget ---
class WeatherWidget(AnimatedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.fade_in()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 12, 15, 12)
        
        # Weather icon ve temp container
        weather_container = QHBoxLayout()
        weather_container.setSpacing(10)
        
        self.weather_icon = QLabel("🌤️")
        self.weather_icon.setFixedSize(50, 50)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        self.weather_icon.setFont(QFont("Segoe UI Emoji", 20))
        self.weather_icon.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                border-radius: 25px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        weather_container.addWidget(self.weather_icon)
        
        # Temperature ve description
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(2)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.temp_label.setStyleSheet("color: #ffffff;")
        temp_layout.addWidget(self.temp_label)
        
        self.desc_label = QLabel("Yükleniyor...")
        self.desc_label.setFont(QFont("Inter", 11, QFont.Normal))
        self.desc_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        self.desc_label.setWordWrap(True)
        temp_layout.addWidget(self.desc_label)
        
        weather_container.addLayout(temp_layout)
        layout.addLayout(weather_container)
        
        # Last updated
        self.updated_label = QLabel("Son Güncelleme: --")
        self.updated_label.setFont(QFont("Inter", 10, QFont.Normal))
        self.updated_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 10px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.updated_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.updated_label)
        
        # Container styling
        self.setStyleSheet("""
            WeatherWidget {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
            }
        """)

# --- Premium Pharmacy Card ---
class PharmacyCard(AnimatedWidget):
    def __init__(self, pharmacy_data, parent=None):
        super().__init__(parent)
        self.pharmacy_data = pharmacy_data
        self.init_ui()
        
    def init_ui(self):
        self.setFixedHeight(650)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Card styling - BEYAZ ARKA PLAN İÇİN UYARLANMIŞ
        self.setStyleSheet("""
            PharmacyCard {
                background-color: rgba(231, 76, 60, 0.1);
                border: 2px solid rgba(231, 76, 60, 0.3);
                border-radius: 25px;
                margin: 10px 20px 25px 20px;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)
        
        # Info section
        info_section = self.create_info_section()
        layout.addWidget(info_section)
        
        # Map section
        if self.pharmacy_data.get('lat_long'):
            map_section = self.create_map_section()
            layout.addWidget(map_section)
    
    def create_info_section(self):
        section = QWidget()
        section.setFixedHeight(240)
        layout = QHBoxLayout(section)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.setSpacing(25)
        
        # Left: Pharmacy information
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(12)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Pharmacy name - BEYAZ ARKA PLAN İÇİN SİYAH METİN
        name_label = QLabel(self.pharmacy_data.get('adi', 'Bilinmeyen Eczane'))
        name_label.setFont(QFont("Inter", 24, QFont.Bold))
        name_label.setStyleSheet("""
            color: #ffffff;
            background: #e74c3c;
            padding: 12px 18px;
            border-radius: 12px;
            border: 2px solid rgba(231, 76, 60, 0.8);
        """)
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # Address - BEYAZ ARKA PLAN İÇİN UYARLANMIŞ
        address_text = self.pharmacy_data.get('adres', 'Adres bilgisi mevcut değil')
        address_label = QLabel(f"📍 {address_text}")
        address_label.setFont(QFont("Inter", 14, QFont.Normal))
        address_label.setStyleSheet("""
            color: #2c3e50;
            background: rgba(231, 76, 60, 0.1);
            padding: 10px 15px;
            border-radius: 15px;
            border: 1px solid rgba(231, 76, 60, 0.3);
        """)
        address_label.setWordWrap(True)
        info_layout.addWidget(address_label)
        
        # Phone - BEYAZ ARKA PLAN İÇİN UYARLANMIŞ
        phone_text = self.pharmacy_data.get('telefon', 'Telefon bilgisi mevcut değil')
        phone_label = QLabel(f"📞 {phone_text}")
        phone_label.setFont(QFont("Inter", 14, QFont.Normal))
        phone_label.setStyleSheet("""
            color: #2c3e50;
            background: rgba(231, 76, 60, 0.1);
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px solid rgba(231, 76, 60, 0.2);
        """)
        phone_label.setWordWrap(True)
        info_layout.addWidget(phone_label)
        
        layout.addWidget(info_widget, 3)
        
        # Right: QR Code
        qr_widget = self.create_qr_widget()
        layout.addWidget(qr_widget, 0)
        
        return section
    
    def create_qr_widget(self):
        qr_container = QWidget()
        qr_container.setFixedSize(130, 130)
        
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setContentsMargins(0, 0, 0, 0)
        
        qr_label = QLabel()
        qr_label.setFixedSize(130, 130)
        qr_label.setAlignment(Qt.AlignCenter)
        
        # Generate QR code - GERÇEK LOKASYON İLE
        lat_long = self.pharmacy_data.get('lat_long')
        if lat_long and 'qrcode' in sys.modules:
            try:
                # Google Maps linki - gerçek lokasyon
                qr_url = f"https://www.google.com/maps/search/?api=1&query={lat_long}"
                print(f"🗺️ QR kod oluşturuluyor: {qr_url}")
                
                qr_img = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=6,
                    border=2,
                )
                qr_img.add_data(qr_url)
                qr_img.make(fit=True)
                
                qr_pil_img = qr_img.make_image(fill_color="white", back_color="transparent")
                
                byte_array = BytesIO()
                qr_pil_img.save(byte_array, format="PNG")
                
                qr_pixmap = QPixmap()
                qr_pixmap.loadFromData(byte_array.getvalue())
                
                qr_label.setPixmap(qr_pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
            except Exception as e:
                print(f"❌ QR kod hatası: {e}")
                qr_label.setText("QR\nKOD\nHATASI")
                qr_label.setStyleSheet("color: #2c3e50; font-size: 12px; font-weight: bold;")
        else:
            qr_label.setText("🗺️\nHARİTA\nLİNKİ")
            qr_label.setStyleSheet("color: #2c3e50; font-size: 14px; font-weight: bold;")
        
        # QR container styling - BEYAZ ARKA PLAN İÇİN UYARLANMIŞ
        qr_container.setStyleSheet("""
            QWidget {
                background-color: rgba(231, 76, 60, 0.15);
                border: 2px solid rgba(231, 76, 60, 0.4);
                border-radius: 18px;
            }
        """)
        
        qr_layout.addWidget(qr_label)
        return qr_container
    
    def create_map_section(self):
        map_widget = QWidget()
        map_widget.setFixedHeight(385)
        
        layout = QVBoxLayout(map_widget)
        layout.setContentsMargins(20, 5, 20, 15)
        
        map_label = QLabel()
        map_label.setFixedHeight(355)
        map_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Generate map - GERÇEK LOKASYON İLE
        lat_long = self.pharmacy_data.get('lat_long')
        if lat_long:
            try:
                print(f"🗺️ Harita oluşturuluyor: {lat_long}")
                
                map_url_parts = [
                    f"https://maps.googleapis.com/maps/api/staticmap?",
                    f"center={lat_long}&zoom=16&size=920x355&scale=2&",
                    f"style=feature:all|element:geometry|color:0x2c3e50&",
                    f"style=feature:all|element:labels.text.fill|color:0xffffff&",
                    f"style=feature:all|element:labels.text.stroke|color:0x2c3e50&",
                    f"style=feature:landscape|element:geometry|color:0x34495e&",
                    f"style=feature:poi|element:geometry|color:0x3498db&",
                    f"style=feature:road|element:geometry|color:0x7f8c8d&",
                    f"style=feature:water|element:geometry|color:0x2980b9&",
                    f"markers=color:0xe74c3c%7Csize:mid%7Clabel:E%7C{lat_long}&",
                    f"key={API_CONFIG['google_maps']}"
                ]
                
                map_url = "".join(map_url_parts)
                
                response = requests.get(map_url, stream=True, timeout=15)
                response.raise_for_status()
                
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                
                if not pixmap.isNull():
                    # Rounded corners
                    rounded_pixmap = QPixmap(pixmap.size())
                    rounded_pixmap.fill(Qt.transparent)
                    
                    painter = QPainter(rounded_pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    
                    path = QPainterPath()
                    path.addRoundedRect(QRectF(rounded_pixmap.rect()), 15, 15)
                    painter.setClipPath(path)
                    painter.drawPixmap(0, 0, pixmap)
                    painter.end()
                    
                    map_label.setPixmap(rounded_pixmap.scaled(
                        QSize(900, 355), 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    ))
                    map_label.setAlignment(Qt.AlignCenter)
                    
                    # Map styling - BEYAZ ARKA PLAN İÇİN UYARLANMIŞ
                    map_label.setStyleSheet("""
                        QLabel {
                            background: rgba(231, 76, 60, 0.05);
                            border: 2px solid rgba(231, 76, 60, 0.2);
                            border-radius: 15px;
                        }
                    """)
                else:
                    self.show_map_error(map_label)
                    
            except Exception as e:
                print(f"Map generation error: {e}")
                self.show_map_error(map_label)
        else:
            self.show_map_error(map_label)
        
        layout.addWidget(map_label)
        return map_widget
    
    def show_map_error(self, map_label):
        map_label.setText("🗺️ KONUM BİLGİSİ\n\nHarita yüklenemedi")
        map_label.setAlignment(Qt.AlignCenter)
        map_label.setFont(QFont("Inter", 16, QFont.Bold))
        map_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: rgba(231, 76, 60, 0.1);
                border: 2px solid rgba(231, 76, 60, 0.3);
                border-radius: 20px;
                padding: 25px;
            }
        """)

# --- Modern Header Component ---
class ModernHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setFixedHeight(180)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(25)
        
        # Logo yükleme - farklı dosya isimleri dene
        self.logo = GlassmorphismLogo()
        
        # Olası logo dosya yolları
        logo_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpeg"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "eczane_logo.png"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "eczane.png"),
            "logo.png",
            "logo.jpg",
            "eczane_logo.png"
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo_pixmap = QPixmap(logo_path)
                    if not logo_pixmap.isNull():
                        self.logo.setPixmap(logo_pixmap)
                        print(f"✅ Logo yüklendi: {logo_path}")
                        logo_loaded = True
                        break
                except Exception as e:
                    print(f"❌ Logo yüklenirken hata ({logo_path}): {e}")
                    continue
        
        if not logo_loaded:
            print("⚠️ Logo dosyası bulunamadı. Varsayılan eczane logosu kullanılıyor.")
            print("📋 Desteklenen dosya isimleri:")
            for path in logo_paths:
                print(f"   - {os.path.basename(path)}")
            
        layout.addWidget(self.logo)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        self.title_label = QLabel("NÖBETÇİ ECZANELER")
        self.title_label.setFont(QFont("Inter", 32, QFont.Bold))
        self.title_label.setStyleSheet("color: #ffffff; background: transparent;")
        title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("KARŞIYAKA 4")
        self.subtitle_label.setFont(QFont("Inter", 18, QFont.Medium))
        self.subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            background: rgba(255, 255, 255, 0.1);
            padding: 6px 15px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        """)
        title_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Weather widget
        self.weather_widget = WeatherWidget()
        self.weather_widget.setFixedWidth(250)
        layout.addWidget(self.weather_widget)
        
        # Header styling - GRİ SİYAH ARKA PLAN
        self.setStyleSheet("ModernHeader { background-color: #2c3e50; border: none; }")

# --- Modern Pharmacy Screen ---
class NobetciEczaneScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui_screen()
        self.setup_timers()
        
        # Load data automatically
        QTimer.singleShot(500, self.load_data)
        
    def init_ui_screen(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = ModernHeader()
        main_layout.addWidget(self.header)
        
        # Scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setContentsMargins(0, 30, 0, 50)
        self.scroll_layout.setSpacing(0)
        self.scroll_area.setWidget(self.scroll_content_widget)
        
        # Scroll styling - BEYAZ ARKA PLAN
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #ffffff;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(0, 0, 0, 0.1);
                width: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #e74c3c;
                border-radius: 7px;
                min-height: 35px;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
            QScrollBar::handle:vertical:hover {
                background-color: #c0392b;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        main_layout.addWidget(self.scroll_area)
        
        # Main background - BEYAZ
        self.setStyleSheet("NobetciEczaneScreen { background-color: #ffffff; }")

    def setup_timers(self):
        # Data refresh timer (2 hours)
        self.data_refresh_timer = QTimer(self)
        self.data_refresh_timer.timeout.connect(self.load_data)
        self.data_refresh_timer.start(7200000)

        # Time update timer
        self.time_update_timer = QTimer(self)
        self.time_update_timer.timeout.connect(self.update_time_label)
        self.time_update_timer.start(1000)

        # Weather update timer (15 minutes)
        self.weather_update_timer = QTimer(self)
        self.weather_update_timer.timeout.connect(self.fetch_weather_data)
        self.weather_update_timer.start(900000)
        
        # Load weather immediately
        QTimer.singleShot(1000, self.fetch_weather_data)

    def update_time_label(self):
        current_time = time.strftime('%d.%m.%Y %H:%M:%S')
        self.header.weather_widget.updated_label.setText(f"Son Güncelleme: {current_time}")

    def get_weather_color(self, temp):
        if temp >= 30:
            return "#ef4444"  # Hot red
        elif 20 <= temp < 30:
            return "#f59e0b"  # Warm orange
        elif 10 <= temp < 20:
            return "#3b82f6"  # Cool blue
        elif 0 <= temp < 10:
            return "#8b5cf6"  # Cold purple
        else:
            return "#6b7280"  # Very cold gray

    def fetch_weather_data(self):
        if not API_CONFIG['openweather']:
            self.header.weather_widget.temp_label.setText("API Eksik")
            self.header.weather_widget.desc_label.setText("API anahtarı gerekli")
            return

        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"q={API_CONFIG['city']}&"
            f"appid={API_CONFIG['openweather']}&"
            f"units=metric&"
            f"lang=tr"
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
                        icon_color = self.get_weather_color(temp)
                        
                        self.header.weather_widget.temp_label.setText(f"{temp:.1f}°C")
                        self.header.weather_widget.desc_label.setText(weather_desc.capitalize())
                        self.header.weather_widget.weather_icon.setStyleSheet(f"""
                            QLabel {{
                                background-color: {icon_color};
                                border-radius: 25px;
                                border: 2px solid rgba(255, 255, 255, 0.3);
                            }}
                        """)
                        
                        print(f"🌤️ Weather updated: {API_CONFIG['city']} - {temp:.1f}°C")
                    else:
                        self.header.weather_widget.temp_label.setText("--°C")
                        self.header.weather_widget.desc_label.setText("Veri eksik")
                else:
                    self.header.weather_widget.temp_label.setText("--°C")
                    self.header.weather_widget.desc_label.setText("Veri hatası")
            else:
                self.header.weather_widget.temp_label.setText("--°C")
                self.header.weather_widget.desc_label.setText("Bağlantı hatası")
                
        except Exception as e:
            self.header.weather_widget.temp_label.setText("--°C")
            self.header.weather_widget.desc_label.setText("Ağ hatası")
            print(f"🌤️ Weather error: {e}")

    def load_data(self):
        print("🔄 Loading modern pharmacy data...")
        self.header.weather_widget.updated_label.setText("Veriler yükleniyor...")
        QApplication.processEvents()

        # Clear existing cards
        self.clear_layout(self.scroll_layout)
        
        # Loading widget
        loading_widget = QWidget()
        loading_widget.setFixedHeight(400)
        loading_layout = QVBoxLayout(loading_widget)
        loading_layout.setAlignment(Qt.AlignCenter)
        
        loading_label = QLabel("🔄 NÖBETÇİ ECZANE VERİLERİ YÜKLENİYOR...")
        loading_label.setFont(QFont("Inter", 28, QFont.Bold))
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("""
            color: #ffffff;
            background: rgba(52, 152, 219, 0.8);
            padding: 50px;
            border: 3px solid rgba(52, 152, 219, 0.9);
            border-radius: 25px;
            margin: 40px;
        """)
        loading_layout.addWidget(loading_label)
        
        progress_label = QLabel("Lütfen bekleyiniz...")
        progress_label.setFont(QFont("Inter", 18, QFont.Normal))
        progress_label.setAlignment(Qt.AlignCenter)
        progress_label.setStyleSheet("color: #ffffff; background: transparent; padding: 20px;")
        loading_layout.addWidget(progress_label)
        
        self.scroll_layout.addWidget(loading_widget)
        QApplication.processEvents()

        # Load pharmacy data
        try:
            pharmacy_list = self.scrape_eczane_data(API_CONFIG['target_region'])
            
            # Clear loading
            self.clear_layout(self.scroll_layout)
            
            if pharmacy_list:
                self.display_pharmacies(pharmacy_list)
                print(f"✅ Loaded {len(pharmacy_list)} pharmacies successfully!")
            else:
                print("❌ No pharmacy data found, showing sample data...")
                sample_data = self.get_sample_pharmacy_data()
                self.display_pharmacies(sample_data)
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.clear_layout(self.scroll_layout)
            self.show_error_message()
            
    def scrape_eczane_data(self, region):
        """Get real pharmacy data from İzmir Eczacı Odası"""
        try:
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pharmacy_list = []
            eczane_elements = soup.find_all('div', class_='col_12_of_12')
            
            if not eczane_elements:
                print("⚠️ No pharmacy elements found, using sample data")
                return self.get_sample_pharmacy_data()
            
            for element in eczane_elements:
                try:
                    name_element = element.find('h4', class_='red')
                    if not name_element:
                        continue
                        
                    full_name = name_element.get_text(strip=True)
                    
                    # Filter for KARŞIYAKA 4 only
                    if "KARŞIYAKA 4" not in full_name.upper():
                        continue
                    
                    # Split name and region
                    if " - " in full_name:
                        eczane_name, bolge = full_name.split(" - ", 1)
                    else:
                        eczane_name = full_name
                        bolge = "KARŞIYAKA 4"
                    
                    # Get address and phone
                    p_element = element.find('p')
                    if not p_element:
                        continue
                    
                    p_text = p_element.get_text(separator=' | ', strip=True)
                    
                    # Parse address and phone
                    adres = "Adres bilgisi bulunamadı"
                    telefon = "Telefon bilgisi bulunamadı"
                    
                    parts = p_text.split(' | ')
                    if len(parts) >= 2:
                        adres = parts[0].strip()
                        telefon = parts[1].strip() if len(parts) > 1 else "Bulunamadı"
                    
                    # Gerçek adresi koordinata çevir
                    coords = self.get_coordinates_from_address(adres, bolge)
                    
                    pharmacy = {
                        "adi": eczane_name.strip().replace("  ", " "),
                        "adres": adres,
                        "telefon": telefon,
                        "lat_long": coords  # Gerçek koordinat
                    }
                    
                    pharmacy_list.append(pharmacy)
                    print(f"  ✅ Found: {eczane_name}")
                    
                except Exception as e:
                    print(f"  ❌ Error parsing pharmacy element: {e}")
                    continue
            
            if pharmacy_list:
                print(f"🎉 Found {len(pharmacy_list)} pharmacy(s) in KARŞIYAKA 4!")
                return pharmacy_list
            else:
                print("⚠️ No KARŞIYAKA 4 pharmacies found, using sample data")
                return self.get_sample_pharmacy_data()
                
        except Exception as e:
            print(f"❌ Error fetching real data: {e}")
            print("⚠️ Falling back to sample data")
            return self.get_sample_pharmacy_data()
    
    def get_sample_pharmacy_data(self):
        """Sample pharmacy data for Karşıyaka 4 region only"""
        print("📋 Generating KARŞIYAKA 4 pharmacy data...")
        return [
            {
                "adi": "💊 NÖBETÇI MERKEZ ECZANESİ",
                "adres": "Atatürk Caddesi No:123, Karşıyaka 4 Bölgesi/İzmir",
                "telefon": "0232 123 45 67",
                "lat_long": "38.4642,27.1285"  # KARŞIYAKA 4 doğru koordinat
            }
        ]

    def show_error_message(self):
        print("❌ Showing error message...")
        error_widget = QWidget()
        error_widget.setFixedHeight(250)
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignCenter)
        
        error_label = QLabel("⚠️ Veri Yüklenemedi\n\nSample veriler gösteriliyor")
        error_label.setFont(QFont("Inter", 28, QFont.Bold))
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("""
            color: #ffffff;
            background-color: rgba(231, 76, 60, 0.3);
            padding: 40px;
            border: 3px solid rgba(231, 76, 60, 0.6);
            border-radius: 25px;
            margin: 50px;
        """)
        
        error_layout.addWidget(error_label)
        self.scroll_layout.addWidget(error_widget)
        
        # Show sample data after 2 seconds
        QTimer.singleShot(2000, lambda: self.display_pharmacies(self.get_sample_pharmacy_data()))

    def display_pharmacies(self, pharmacy_list):
        print(f"🏥 Displaying {len(pharmacy_list)} pharmacies...")
        if not pharmacy_list:
            print("❌ No pharmacy list provided!")
            return

        # Clear existing content
        self.clear_layout(self.scroll_layout)

        # Add cards with animation - NO INTERACTION
        for i, pharmacy in enumerate(pharmacy_list):
            print(f"  📍 Adding: {pharmacy.get('adi', 'Unknown')}")
            try:
                card = PharmacyCard(pharmacy)
                self.scroll_layout.addWidget(card)
                
                # Staggered fade-in animation only
                QTimer.singleShot(i * 400, lambda c=card: c.fade_in())
                
            except Exception as e:
                print(f"❌ Error creating card for {pharmacy.get('adi', 'Unknown')}: {e}")
                
        print("✅ All pharmacy cards added!")

    def clear_layout(self, layout):
        """Clear all widgets from layout"""
        print(f"🧹 Clearing layout (has {layout.count()} items)...")
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())
        print("✅ Layout cleared!")

# --- Premium Ad Screen ---
class AdScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.video_files = []
        self.current_video_index = 0
        self.init_ui_screen()

    def init_ui_screen(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        # Media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.error.connect(self.media_error)

        # Styling
        self.setStyleSheet("""
            AdScreen {
                background-color: #2c3e50;
            }
            QVideoWidget {
                background: transparent;
                border-radius: 15px;
            }
        """)

        # Loading screen
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignCenter)
        
        self.loading_title = QLabel("🎬 REKLAM EKRANI")
        self.loading_title.setFont(QFont("Inter", 64, QFont.Bold))
        self.loading_title.setAlignment(Qt.AlignCenter)
        self.loading_title.setStyleSheet("""
            color: #ffffff;
            background-color: rgba(255, 255, 255, 0.1);
            padding: 80px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 35px;
            margin: 120px;
        """)
        
        self.status_label = QLabel("Reklamlar hazırlanıyor...")
        self.status_label.setFont(QFont("Inter", 28, QFont.Normal))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            background: transparent;
            padding: 30px;
        """)
        
        loading_layout.addWidget(self.loading_title)
        loading_layout.addWidget(self.status_label)
        layout.addWidget(self.loading_widget)
        
        self.video_widget.hide()

    def load_videos(self):
        ads_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ads")
        
        if not os.path.exists(ads_folder):
            os.makedirs(ads_folder)
            self.status_label.setText("❌ 'ads' klasörü oluşturuldu\nVideo dosyalarını ekleyin")
            return

        supported_formats = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')
        self.video_files = [
            os.path.join(ads_folder, f) 
            for f in os.listdir(ads_folder) 
            if f.lower().endswith(supported_formats)
        ]
        
        if not self.video_files:
            self.status_label.setText("❌ Video bulunamadı\n'ads' klasörüne video dosyalarını ekleyin")
        else:
            self.loading_widget.hide()
            self.video_widget.show()
            self.current_video_index = 0
            print(f"Loaded {len(self.video_files)} advertisement videos")

    def play_next_video(self):
        if not self.video_files:
            self.status_label.setText("❌ Oynatılacak video yok")
            self.loading_widget.show()
            self.video_widget.hide()
            return
        
        if self.current_video_index >= len(self.video_files):
            self.current_video_index = 0
        
        video_path = self.video_files[self.current_video_index]
        print(f"Playing advertisement: {os.path.basename(video_path)}")
        
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.media_player.play()
        self.current_video_index += 1

    def media_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            QTimer.singleShot(1000, self.play_next_video)

    def media_error(self, error):
        error_msg = self.media_player.errorString()
        print(f"Video playback error: {error_msg}")
        
        self.status_label.setText(f"⚠️ Video oynatma hatası\n{error_msg[:50]}...\n\nSonraki videoya geçiliyor...")
        self.loading_widget.show()
        self.video_widget.hide()
        
        QTimer.singleShot(3000, self.play_next_video)

# --- Modern Main Application ---
class EczaneApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Nöbetçi Eczane Vitrin Ekranı")
        self.setGeometry(100, 50, 1200, 1600)
        
        # For production use fullscreen
        # self.showFullScreen()
        # self.setCursor(Qt.BlankCursor)

        self.main_app_layout = QVBoxLayout(self)
        self.main_app_layout.setContentsMargins(0, 0, 0, 0)
        self.main_app_layout.setSpacing(0)
        
        # Screen stack
        self.screen_stack = QStackedLayout()
        self.main_app_layout.addLayout(self.screen_stack)

        # Initialize screens
        self.nobetci_eczane_screen = NobetciEczaneScreen()
        self.screen_stack.addWidget(self.nobetci_eczane_screen)

        self.ad_screen = AdScreen()
        self.screen_stack.addWidget(self.ad_screen)

        # Screen switching timer
        self.screen_timer = QTimer(self)
        self.screen_timer.timeout.connect(self.check_display_mode)
        self.screen_timer.start(10000)

        # Initialize with pharmacy screen
        self.check_display_mode()

    def check_display_mode(self):
        # For demo - always show pharmacy screen
        if self.screen_stack.currentWidget() != self.nobetci_eczane_screen:
            print("🔄 Switching to Modern Pharmacy Screen")
            self.screen_stack.setCurrentWidget(self.nobetci_eczane_screen)
            self.nobetci_eczane_screen.load_data()
            self.ad_screen.media_player.stop()
        return

    def keyPressEvent(self, event):
        """Handle keyboard events for admin control only"""
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
                self.setCursor(Qt.ArrowCursor)
            else:
                self.close()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
                self.setCursor(Qt.ArrowCursor)
            else:
                self.showFullScreen()
                self.setCursor(Qt.BlankCursor)
        elif event.key() == Qt.Key_F5:
            if isinstance(self.screen_stack.currentWidget(), NobetciEczaneScreen):
                self.nobetci_eczane_screen.load_data()
        
        super().keyPressEvent(event)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Modern Nöbetçi Eczane Ekranı")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Modern Pharmacy Display")
    
    # Global styling
    app.setStyleSheet("""
        * {
            font-family: 'Inter', 'SF Pro Display', 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            font-weight: 400;
            letter-spacing: 0.3px;
        }
        QToolTip {
            background: rgba(0, 0, 0, 0.9);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 12px;
            font-size: 14px;
            font-weight: 500;
        }
    """)
    
    # Create and show main window
    window = EczaneApp()
    window.show()
    
    print("🚀 Modern Vitrin Ekranı başlatıldı!")
    print("🖥️  SADECE GÖSTERIM AMAÇLI - ETKİLEŞİM YOK")
    print("📋 Admin Kontrolleri:")
    print("   ESC: Çıkış / Tam ekrandan çık")
    print("   F11: Tam ekran aç/kapat")
    print("   F5:  Verileri yenile (admin)")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
