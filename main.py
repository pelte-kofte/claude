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

class ModernCorporateEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane - Modern Corporate")
        
        # DİKEY MONİTÖR İÇİN BOYUTLAR - GENİŞLETİLDİ
        self.setFixedSize(900, 1280)  # 720'den 900'e genişletildi (+180px)
        
        # API anahtarları
        self.api_key = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
        self.weather_api_key = "b0d1be7721b4967d8feb810424bd9b6f"
        self.start_lat = 38.47434762293852
        self.start_lon = 27.112356625119595
        
        self.current_mode = None
        self.video_path = None
        
        # 🎨 MODERN CORPORATE RENK PALETİ - PROFESYONEL
        self.colors = {
            'bg_primary': '#000000',       # Pure black background
            'bg_secondary': '#111111',     # Soft black
            'bg_card': '#1a1a1a',         # Card background
            'bg_accent': '#222222',       # Accent background
            
            'text_primary': '#ffffff',     # Pure white text
            'text_secondary': '#cccccc',   # Light gray text
            'text_muted': '#888888',       # Muted gray text
            
            'accent_blue': '#007AFF',      # Apple blue
            'accent_green': '#30D158',     # Success green
            'accent_orange': '#FF9500',    # Warning orange
            'accent_red': '#FF3B30',       # Error red
            'accent_purple': '#AF52DE',    # Purple accent
            
            'border': '#333333',           # Subtle borders
            'border_light': '#444444',     # Lighter borders
            
            'shadow': 'rgba(0, 0, 0, 0.5)', # Subtle shadows
            'hover': 'rgba(255, 255, 255, 0.05)', # Hover effect
        }
        
        self.setup_ui()
        self.setup_video_player()
        self.setup_timers()
        self.switch_to_pharmacy_mode()
        
        self.show()
        print("🏢 Modern Corporate Pharmacy Monitor başlatıldı!")

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
        """🏢 MODERN CORPORATE DESIGN - Apple/Tesla Style"""
        widget = self.pharmacy_widget
        
        # CORPORATE BACKGROUND
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['bg_primary']};
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                color: {self.colors['text_primary']};
            }}
        """)
        
        # SCROLL AREA - MINIMAL STYLE
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
        
        # İÇERİK WİDGETİ
        content_widget = QWidget()
        content_widget.setMinimumHeight(1400)
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 32)  # Yan marginler artırıldı
        
        # 🎬 ANİMASYON SİSTEMLERİ ÖNCE SETUP ET
        self.setup_animations()
        
        # SECTIONS
        self.create_red_header(layout)
        self.create_corporate_info_section(layout)
        self.create_corporate_qr_map_section(layout)
        self.create_corporate_footer(layout)
        
        # BOŞ ALAN
        spacer = QWidget()
        spacer.setMinimumHeight(100)
        spacer.setStyleSheet("background: transparent;")
        layout.addWidget(spacer)
        
        scroll_area.setWidget(content_widget)
        
        main_widget_layout = QVBoxLayout(widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.addWidget(scroll_area)

    def create_red_header(self, layout):
        """🔴 KIRMIZI HEADER - DÜZELTİLMİŞ VERSİYON"""
        header = QWidget()
        header.setFixedHeight(140)  # 120'den 140'a yükseltildi
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC143C, stop:0.5 #B22222, stop:1 #8B0000);
                border: none;
                border-radius: 16px;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)  # Sol/sağ margin azaltıldı
        header_layout.setSpacing(20)  # Spacing azaltıldı
        
        # SOL: Logo + Başlık - KOMPAKT
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_layout = QHBoxLayout(left_widget)
        left_layout.setSpacing(16)  # Spacing azaltıldı
        
        # LOGO - KÜÇÜK
        self.logo_label = QLabel()
        self.load_logo()
        self.logo_label.setStyleSheet("""
            background: transparent;
            border-radius: 35px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(70, 70)  # 80'den 70'e küçültüldü
        left_layout.addWidget(self.logo_label)
        
        # BAŞLIK - KÜÇÜK FONT
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(4)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        main_title = QLabel("KARŞIYAKA 4")
        main_title.setFont(QFont('Segoe UI', 26, QFont.Bold))  # 32'den 26'ya küçültüldü
        main_title.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("Nöbetçi Eczane Sistemi")
        sub_title.setFont(QFont('Segoe UI', 13, QFont.Medium))  # 16'dan 13'e küçültüldü
        sub_title.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        title_layout.addWidget(sub_title)
        
        left_layout.addWidget(title_widget)
        header_layout.addWidget(left_widget, 2)
        
        # SAĞ: Saat/Tarih + Sıcaklık - HİZALANMIŞ
        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 8, 0, 8)  # Üst/alt padding
        
        # ÜST: SAAT + TARİH YAN YANA - PERFECT HİZALAMA
        datetime_row = QWidget()
        datetime_row.setStyleSheet("background: transparent;")
        datetime_row_layout = QHBoxLayout(datetime_row)
        datetime_row_layout.setSpacing(8)
        datetime_row_layout.setContentsMargins(0, 0, 0, 0)
        datetime_row_layout.addStretch()  # Sağa yasla
        
        # SAAT
        self.time_display = QLabel()
        self.time_display.setFont(QFont('Segoe UI', 22, QFont.Bold))
        self.time_display.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        self.time_display.setAlignment(Qt.AlignRight)
        datetime_row_layout.addWidget(self.time_display)
        
        # NOKTA - ORTADA
        bullet = QLabel("•")
        bullet.setFont(QFont('Segoe UI', 22, QFont.Bold))  # Aynı font size
        bullet.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            background: transparent;
        """)
        bullet.setAlignment(Qt.AlignCenter)
        datetime_row_layout.addWidget(bullet)
        
        # TARİH
        self.date_display = QLabel()
        self.date_display.setFont(QFont('Segoe UI', 18, QFont.Medium))  # 20'den 18'e küçültüldü
        self.date_display.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        self.date_display.setAlignment(Qt.AlignLeft)
        datetime_row_layout.addWidget(self.date_display)
        
        right_layout.addWidget(datetime_row)
        
        # ALT: SICAKLIK + WEATHER ICON - HİZALANMIŞ
        weather_row = QWidget()
        weather_row.setStyleSheet("background: transparent;")
        weather_row_layout = QHBoxLayout(weather_row)
        weather_row_layout.setSpacing(8)
        weather_row_layout.setContentsMargins(0, 0, 0, 0)
        weather_row_layout.addStretch()  # Sağa yasla
        
        # WEATHER ICON
        self.weather_icon = QLabel("☀")
        self.weather_icon.setFont(QFont('Segoe UI', 18))  # 20'den 18'e küçültüldü
        self.weather_icon.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        self.weather_icon.setAlignment(Qt.AlignCenter)
        weather_row_layout.addWidget(self.weather_icon)
        
        # SICAKLIK
        self.weather_temp = QLabel("34°C")
        self.weather_temp.setFont(QFont('Segoe UI', 18, QFont.Bold))  # 20'den 18'e küçültüldü
        self.weather_temp.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        weather_row_layout.addWidget(self.weather_temp)
        
        right_layout.addWidget(weather_row)
        header_layout.addWidget(right_widget, 1)
        
        layout.addWidget(header)
        
        # Saat timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def create_corporate_info_section(self, layout):
        """📋 CORPORATE INFO SECTION - QR Sağda (ÇİZGİSİZ)"""
        info_container = QWidget()
        info_container.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border: none;
            border-radius: 16px;
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(32, 24, 32, 24)
        info_layout.setSpacing(20)
        
        # BAŞLIK - CORPORATE STYLE (ÇİZGİSİZ)
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
        
        # İÇERİK + QR - YATAY LAYOUT
        content_row = QWidget()
        content_row.setStyleSheet("background: transparent;")
        content_row_layout = QHBoxLayout(content_row)
        content_row_layout.setSpacing(24)
        
        # SOL: ECZANE BİLGİLERİ (ÇİZGİSİZ)
        self.info_label = QLabel("Yükleniyor...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Segoe UI', 16))
        self.info_label.setStyleSheet(f"""
            color: {self.colors['text_primary']};
            background-color: {self.colors['bg_secondary']};
            border: none;
            border-radius: 12px;
            padding: 24px;
            line-height: 28px;
        """)
        self.info_label.setMinimumHeight(200)
        self.info_label.setMaximumHeight(250)
        content_row_layout.addWidget(self.info_label, 2)  # 2/3 genişlik
        
        # SAĞ: QR KOD (ÇİZGİSİZ VE HİZALI)
        qr_widget = QWidget()
        qr_widget.setStyleSheet("background: transparent;")
        qr_widget_layout = QVBoxLayout(qr_widget)
        qr_widget_layout.setSpacing(12)
        qr_widget_layout.setContentsMargins(0, 0, 0, 0)  # Margin temizlendi
        
        # QR TITLE - HİZALI
        qr_title = QLabel("YOL TARİFİ İÇİN\nQR OKUTUNUZ")
        qr_title.setFont(QFont('Segoe UI', 12, QFont.Bold))
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            background: transparent;
            padding: 8px;
        """)
        qr_widget_layout.addWidget(qr_title)
        
        # QR KOD - MÜKEMMEL HİZALAMA
        qr_container = QWidget()
        qr_container.setStyleSheet("background: transparent;")
        qr_container_layout = QHBoxLayout(qr_container)
        qr_container_layout.setContentsMargins(0, 0, 0, 0)
        qr_container_layout.addStretch()  # Sol boşluk
        
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
        qr_container_layout.addStretch()  # Sağ boşluk
        
        qr_widget_layout.addWidget(qr_container)
        qr_widget_layout.addStretch()  # Alt boşluk
        
        content_row_layout.addWidget(qr_widget, 1)  # 1/3 genişlik
        
        info_layout.addWidget(content_row)
        layout.addWidget(info_container)

    def create_corporate_qr_map_section(self, layout):
        """🗺️ BÜYÜK HARİTA - Tek başına"""
        # MAP CONTAINER - BÜYÜK
        map_container = QWidget()
        map_container.setStyleSheet(f"""
            background-color: {self.colors['bg_card']};
            border: none;
            border-radius: 16px;
        """)
        
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(24, 24, 24, 24)
        map_layout.setSpacing(16)
        
        # MAP TITLE
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
        
        # BÜYÜK HARİTA - LOADING SPINNER İLE
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(300)
        self.map_label.setMaximumHeight(350)
        self.map_label.setStyleSheet(f"""
            background-color: {self.colors['bg_secondary']};
            border: none;
            border-radius: 12px;
            color: {self.colors['text_secondary']};
            font-size: 18px;
        """)
        # Başlangıç loading mesajı
        self.show_loading_spinner()
        map_layout.addWidget(self.map_label)
        
        layout.addWidget(map_container)

    def create_corporate_footer(self, layout):
        """🏢 CORPORATE FOOTER - Status Bar"""
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
        
        # STATUS INDICATOR - PULSE ANİMASYONLU
        self.status_label = QLabel("● SİSTEM AKTİF")
        self.status_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.status_label.setStyleSheet(f"""
            color: {self.colors['accent_green']};
            background: transparent;
        """)
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        powered_label = QLabel("Powered by AI")
        powered_label.setFont(QFont('Segoe UI', 12, QFont.Medium))
        powered_label.setStyleSheet(f"""
            color: {self.colors['text_muted']};
            background: transparent;
        """)
        footer_layout.addWidget(powered_label)
        
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
                        scaled_logo = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Logo küçültüldü
                        self.logo_label.setPixmap(scaled_logo)
                        logo_loaded = True
                        print(f"✅ Logo yüklendi: {path}")
                        break
            if not logo_loaded:
                self.logo_label.setText("🏥")
                self.logo_label.setFont(QFont('Segoe UI', 24))  # Emoji küçültüldü
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
        """Saat ve tarih güncelle - KIRMIZI HEADER İÇİN"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%d.%m.%Y")
        
        if hasattr(self, 'time_display'):
            self.time_display.setText(time_str)
        if hasattr(self, 'date_display'):
            self.date_display.setText(date_str)

    def setup_video_ui(self):
        """Video UI - VİDEO SORUNU DÜZELTİLDİ"""
        widget = self.video_widget
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        widget.setStyleSheet(f"background-color: {self.colors['bg_primary']};")
        
        self.video_widget_display = QVideoWidget()
        layout.addWidget(self.video_widget_display)
        
        # VİDEO BULUNAMADI MESAJI - DÜZELTİLDİ
        self.no_video_label = QLabel()
        self.no_video_label.setAlignment(Qt.AlignCenter)
        self.no_video_label.setFont(QFont('Segoe UI', 28, QFont.Bold))
        self.no_video_label.setStyleSheet(f"""
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
            padding: 50px;
        """)
        # Varsayılan mesaj
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
        # Eczane bilgileri güncelleme - 30 dakika
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(1800000)

        # Nöbet saatleri kontrolü - her dakika
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule_and_switch)
        self.schedule_timer.start(60000)
        
        print("⏰ Nöbet saatleri kontrolü aktif: 18:45-08:45")

    def setup_animations(self):
        """🎬 ANİMASYON SİSTEMLERİ KURULUM"""
        # 💓 PULSE ANİMASYON TİMER - Status için
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_animation)
        self.pulse_timer.start(1000)  # 1 saniye
        self.pulse_state = True
        
        # 🔄 SPINNER ANİMASYON TİMER - Loading için  
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.spinner_animation)
        self.spinner_angle = 0
        self.is_loading = False
        
        print("🎬 Animasyon sistemleri başlatıldı!")

    def pulse_animation(self):
        """💓 PULSE EFEKT - Status indicator için"""
        if hasattr(self, 'status_label'):
            if self.pulse_state:
                # PARLAK HAL
                self.status_label.setStyleSheet(f"""
                    color: {self.colors['accent_green']};
                    background: rgba(48, 209, 88, 0.2);
                    border-radius: 8px;
                    padding: 4px 8px;
                    font-weight: bold;
                """)
            else:
                # NORMAL HAL
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
        self.spinner_timer.start(100)  # 100ms hızlı döngü

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
            
            if self.spinner_angle > 100:  # Reset
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
        """Eczane verisi çek"""
        try:
            print("📡 Eczane bilgileri güncelleniyor...")
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
                    
                    # CORPORATE STYLE BİLGİ FORMATLANMASI
                    info_text = f"""
{name}

📞 Telefon: {phone}

📍 Adres: {address}

🚗 Mesafe: {distance}
⏱️ Süre: {duration}

KARŞIYAKA 4 BÖLGE NÖBET ECZANESI
                    """.strip()
                    
                    self.info_label.setText(info_text)
                    
                    # QR kod oluştur
                    if maps_url:
                        self.create_qr_code(maps_url)
                    
                    # Harita oluştur
                    self.create_route_map(end_lat, end_lon)
                    
                    # Son güncelleme
                    now = datetime.now()
                    self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')}")
                    
                    print("✅ Eczane bilgileri güncellendi")
                    return
            
            # Bulunamadı
            self.info_label.setText("Bugün KARŞIYAKA 4'te nöbetçi eczane bulunamadı.\n\nLütfen daha sonra tekrar kontrol edin.")
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")
            
        except Exception as e:
            self.info_label.setText(f"Bağlantı hatası: {str(e)}\n\nİnternet bağlantısını kontrol edin.")
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Hata)")
            print(f"❌ Güncelleme hatası: {e}")

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
                    
                    # ZOOM ÇOK DAHA YAKIN - SOKAK SEVİYESİ
                    distance_value = route['legs'][0]['distance']['value']
                    
                    if distance_value < 500:  # 500m altı
                        zoom_level = 19  # Maksimum yakın
                    elif distance_value < 800:  # 800m altı  
                        zoom_level = 18  # Çok yakın
                    elif distance_value < 1200:  # 1.2km altı
                        zoom_level = 17  # Yakın sokak
                    elif distance_value < 2000:  # 2km altı (SENİN DURUMUN)
                        zoom_level = 16  # ÇOOK DAHA YAKIN!
                    elif distance_value < 3000:  # 3km altı
                        zoom_level = 15  # Yakın
                    else:
                        zoom_level = 14  # Normal
                    
                    # BÜYÜK HARİTA İÇİN BOYUT - GENİŞLETİLDİ
                    map_width = 820   # 640'tan 820'ye (+180px)
                    map_height = 300  # Aynı yükseklik
                    
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
                    
                    # Harita resmini indir
                    map_response = requests.get(static_map_url, timeout=10)
                    
                    if map_response.status_code == 200:
                        # 🔄 SPINNER DURDUR
                        self.hide_loading_spinner()
                        
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        
                        scaled_pixmap = pixmap.scaled(820, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.map_label.setPixmap(scaled_pixmap)
                        
                        print("✅ Corporate harita oluşturuldu")
                        return
                        
        except Exception as e:
            print(f"Harita hatası: {e}")
            
        # HATA DURUMUNDA SPINNER DURDUR
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
        """🌤️ Hava durumu çek + BASİT EMOJI ICON"""
        try:
            print("🌡️ Hava durumu alınıyor...")
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
            
            # 🌟 BASİT EMOJI WEATHER ICON
            weather_emoji = self.get_weather_emoji(weather_main, temp)
            
            self.weather_temp.setText(f"{temp}°C")
            self.weather_icon.setText(weather_emoji)
            
            print(f"✅ Hava durumu: {temp}°C - {desc} - {weather_emoji}")
            
        except Exception as e:
            self.weather_temp.setText("--°C")
            self.weather_icon.setText("❓")
            print(f"Hava durumu hatası: {e}")

    def get_weather_emoji(self, weather_main, temp):
        """🌟 BASİT EMOJI WEATHER ICONS"""
        
        # 🌞 GÜNEŞ DURUMLARI
        if weather_main in ['clear', 'sunny']:
            if temp >= 30:
                return "🔥"  # Çok sıcak
            elif temp >= 25:
                return "☀"   # Sıcak
            else:
                return "🌤"   # Ilık
                
        # ☁️ BULUTLU DURUMLAR
        elif weather_main in ['clouds', 'partly cloudy']:
            return "☁"
                
        # 🌧️ YAĞMUR DURUMLARI
        elif weather_main in ['rain', 'drizzle']:
            return "🌧"
            
        # ⛈️ FIRTINA
        elif weather_main in ['thunderstorm', 'storm']:
            return "⚡"
            
        # 🌫️ SİS/DUMAN
        elif weather_main in ['mist', 'fog', 'haze']:
            return "🌫"
            
        # ❄️ KAR
        elif weather_main in ['snow']:
            return "❄"
            
        # 🌪️ RÜZGAR
        elif weather_main in ['wind']:
            return "💨"
            
        # DEFAULT
        else:
            return "🌈"

    def create_qr_code(self, url):
        """QR kod oluştur"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            # CORPORATE QR DESIGN - High Contrast
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
    print("🏢 Modern Corporate Pharmacy Monitor")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # CORPORATE FONT SETUP
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    try:
        window = ModernCorporateEczaneApp()
        print("✅ Modern corporate tasarım oluşturuldu")
        print("📐 Dikey format: 900x1280")
        print("🔴 Kırmızı header - Saat/Tarih yan yana")
        print("🎨 Segoe UI font family")
        print("⌨️  ESC: Çıkış, F11: Tam ekran")
        print("🔄 30 dakikada otomatik güncelleme")
        print("=" * 50)
        print("🚀 KIRMIZI HEADER ÇALIŞIYOR!")
        
        app.exec_()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
