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

class ElegantVerticalEczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane - Modern Glassmorphism")
        
        # DİKEY MONİTÖR İÇİN BOYUTLAR - ZORUNLU DİKEY
        self.setFixedSize(720, 1280)  # Fixed size - zorla dikey
        
        # API anahtarları
        self.api_key = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
        self.weather_api_key = "b0d1be7721b4967d8feb810424bd9b6f"
        self.start_lat = 38.47434762293852
        self.start_lon = 27.112356625119595
        
        self.current_mode = None
        self.video_path = None
        
        # 🎨 NORMAL ELEGANT RENK PALETİ (MOR FESTIVAL İPTAL)
        self.colors = {
            'primary': '#1a1a2e',          # Ana koyu
            'secondary': '#16213e',        # İkincil koyu  
            'accent': '#e94560',           # Kırmızı vurgu
            'gold': '#ffd700',             # Altın
            'white': '#ffffff',            # Beyaz
            'light_gray': '#f8f9fa',       # Açık gri
            'dark_gray': '#2c3e50',        # Koyu gri
            'glass': 'rgba(255, 255, 255, 0.12)',  # Glass efekt
            'glass_dark': 'rgba(0, 0, 0, 0.2)',    # Koyu glass
            'shadow_light': 'rgba(255, 255, 255, 0.1)',  # Açık gölge
            'shadow_dark': 'rgba(0, 0, 0, 0.3)',         # Koyu gölge
            'blue': '#3498db',             # Normal mavi
            'green': '#00ff88',            # Yeşil
            'orange': '#f39c12'            # Turuncu
        }
        
        self.setup_ui()
        self.setup_video_player()
        self.setup_timers()
        self.switch_to_pharmacy_mode()
        
        # TAM EKRAN MODU - DİKEY
        self.show()  # Normal window önce
        
        print("🌟 Modern Glassmorphism Pharmacy Monitor başlatıldı!")

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
        """🎨 MODERN GLASSMORPHISM DESIGN - Dikey ekran optimize"""
        widget = self.pharmacy_widget
        
        # SCROLL AREA EKLE - ZORUNLU SCROLL
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # İÇERİK WİDGETİ - YETERLİ YÜKSEK
        content_widget = QWidget()
        content_widget.setMinimumHeight(1400)
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)  # Spacing artırıldı
        layout.setContentsMargins(20, 20, 20, 20)  # Margin artırıldı
        
        # 🌌 NORMAL BACKGROUND - MOR FESTIVAL İPTAL
        widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['primary']}, 
                    stop:0.3 {self.colors['secondary']}, 
                    stop:1 {self.colors['primary']});
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                margin: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['blue']}, 
                    stop:1 {self.colors['accent']});
                border-radius: 6px;
                min-height: 30px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['gold']}, 
                    stop:1 {self.colors['accent']});
                box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: transparent;
                border: none;
            }}
        """)
        
        # HEADER - MODERN GLASSMORPHISM
        self.create_modern_header(layout)
        
        # ECZANE BİLGİLERİ - DEPTH CARD
        self.create_modern_info_section(layout)
        
        # QR + HARİTA - FLOATING CARDS
        self.create_modern_qr_map_section(layout)
        
        # FOOTER - GLASS BOTTOM
        self.create_modern_footer(layout)
        
        # BOŞ ALAN EKLE - SCROLL İÇİN
        spacer = QWidget()
        spacer.setMinimumHeight(100)
        spacer.setStyleSheet("background: transparent;")
        layout.addWidget(spacer)
        
        # Scroll area'ya ekle
        scroll_area.setWidget(content_widget)
        
        # Ana layout
        main_widget_layout = QVBoxLayout(widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.addWidget(scroll_area)

    def create_modern_header(self, layout):
        """🌟 MODERN GLASSMORPHISM HEADER - ADVANCED SHADOWS"""
        header = QWidget()
        header.setFixedHeight(200)  # Biraz büyüttük
        
        # 🎨 ADVANCED GLASSMORPHISM STYLE
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.25), 
                    stop:0.5 rgba(255, 255, 255, 0.15), 
                    stop:1 rgba(255, 255, 255, 0.1));
                border-radius: 25px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                /* 🌟 MULTIPLE LAYERED SHADOWS */
                box-shadow: 
                    /* Ana gölge */
                    0 20px 40px rgba(0, 0, 0, 0.3),
                    /* İç gölge - glassmorphism */
                    inset 0 1px 0 rgba(255, 255, 255, 0.4),
                    inset 0 -1px 0 rgba(0, 0, 0, 0.2),
                    /* Renkli glow */
                    0 0 60px rgba(233, 69, 96, 0.2),
                    /* Derinlik gölgesi */
                    0 30px 60px rgba(102, 126, 234, 0.15);
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 25, 30, 25)
        header_layout.setSpacing(25)
        
        # SOL: Logo + Başlık - FLOATING EFFECT
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_layout = QHBoxLayout(left_widget)
        left_layout.setSpacing(25)
        
        # 🔮 LOGO - GLASSMORPHISM CIRCLE
        self.logo_label = QLabel()
        self.load_logo()
        self.logo_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 215, 0, 0.3),
                stop:0.5 rgba(255, 255, 255, 0.2),
                stop:1 rgba(233, 69, 96, 0.3));
            border-radius: 45px;
            padding: 25px;
            border: 3px solid rgba(255, 255, 255, 0.4);
            /* 🌟 LOGO SHADOW EFFECTS */
            box-shadow: 
                0 15px 35px rgba(255, 215, 0, 0.4),
                inset 0 2px 0 rgba(255, 255, 255, 0.6),
                inset 0 -2px 0 rgba(0, 0, 0, 0.2),
                0 0 30px rgba(255, 215, 0, 0.3);
        """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(90, 90)
        left_layout.addWidget(self.logo_label)
        
        # ✨ BAŞLIK - TEXT SHADOW EFFECTS
        title_widget = QWidget()
        title_widget.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(8)
        
        main_title = QLabel("KARŞIYAKA 4")
        main_title.setFont(QFont('Segoe UI', 32, QFont.Bold))
        main_title.setStyleSheet(f"""
            color: {self.colors['white']};
            background: transparent;
            /* 🌟 TEXT SHADOW DEPTH */
            text-shadow: 
                2px 2px 4px rgba(0, 0, 0, 0.7),
                0 0 15px rgba(255, 255, 255, 0.3),
                0 0 30px rgba(233, 69, 96, 0.2);
        """)
        title_layout.addWidget(main_title)
        
        sub_title = QLabel("NÖBETÇİ ECZANE")
        sub_title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        sub_title.setStyleSheet(f"""
            color: {self.colors['gold']};
            background: transparent;
            text-shadow: 
                1px 1px 3px rgba(0, 0, 0, 0.8),
                0 0 20px rgba(255, 215, 0, 0.4);
        """)
        title_layout.addWidget(sub_title)
        
        left_layout.addWidget(title_widget)
        header_layout.addWidget(left_widget, 2)
        
        # SAĞ: Saat + Hava - FLOATING CARDS
        right_widget = QWidget()
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # ⏰ SAAT - GLASSMORPHISM CARD
        self.time_label = QLabel()
        self.time_label.setFont(QFont('SF Mono', 22, QFont.Bold))
        self.time_label.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.2),
                stop:1 rgba(255, 255, 255, 0.1));
            color: {self.colors['white']};
            border-radius: 15px;
            padding: 15px 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            /* 🌟 TIME CARD SHADOWS */
            box-shadow: 
                0 10px 25px rgba(0, 0, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.4),
                0 0 25px rgba(0, 210, 255, 0.2);
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.time_label)
        
        # 🌤️ HAVA DURUMU - FLOATING CARD
        weather_widget = QWidget()
        weather_widget.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.15),
                stop:1 rgba(255, 255, 255, 0.05));
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.25);
            padding: 15px;
            /* 🌟 WEATHER CARD SHADOWS */
            box-shadow: 
                0 12px 30px rgba(0, 0, 0, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.3),
                0 0 20px rgba(52, 152, 219, 0.15);
        """)
        weather_layout = QHBoxLayout(weather_widget)
        weather_layout.setSpacing(15)
        
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setFont(QFont('Segoe UI', 22, QFont.Bold))
        self.weather_temp.setStyleSheet(f"""
            color: {self.colors['gold']};
            background: transparent;
            text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
        """)
        weather_layout.addWidget(self.weather_temp)
        
        self.weather_desc = QLabel("Yükleniyor...")
        self.weather_desc.setFont(QFont('Segoe UI', 16))
        self.weather_desc.setStyleSheet(f"""
            color: {self.colors['white']};
            background: transparent;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        """)
        weather_layout.addWidget(self.weather_desc)
        
        right_layout.addWidget(weather_widget)
        header_layout.addWidget(right_widget, 1)
        
        layout.addWidget(header)
        
        # Saat timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def create_modern_info_section(self, layout):
        """💎 MODERN INFO SECTION - DEPTH GLASSMORPHISM"""
        info_container = QWidget()
        info_container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 255, 255, 0.2),
                stop:0.5 rgba(255, 255, 255, 0.1),
                stop:1 rgba(255, 255, 255, 0.05));
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            /* 🌟 ADVANCED INFO CARD SHADOWS */
            box-shadow: 
                /* Ana derinlik gölgesi */
                0 25px 50px rgba(0, 0, 0, 0.3),
                /* İç ışıltı */
                inset 0 2px 0 rgba(255, 255, 255, 0.4),
                inset 0 -2px 0 rgba(0, 0, 0, 0.15),
                /* Renkli glow efektler */
                0 0 40px rgba(233, 69, 96, 0.15),
                0 0 80px rgba(102, 126, 234, 0.1),
                /* Backdrop blur simulation */
                0 30px 80px rgba(0, 0, 0, 0.2);
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(25, 20, 25, 20)
        info_layout.setSpacing(15)
        
        # 🏷️ BAŞLIK - NEON EFFECT
        title = QLabel("📍 NÖBETÇİ ECZANE BİLGİLERİ")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet(f"""
            color: {self.colors['gold']};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 215, 0, 0.1),
                stop:0.5 rgba(233, 69, 96, 0.1),
                stop:1 rgba(255, 215, 0, 0.1));
            padding: 12px;
            border-radius: 12px;
            border: 2px solid rgba(255, 215, 0, 0.4);
            /* 🌟 TITLE GLOW */
            text-shadow: 
                0 0 20px rgba(255, 215, 0, 0.8),
                0 0 40px rgba(233, 69, 96, 0.3);
            box-shadow: 
                0 8px 20px rgba(255, 215, 0, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        """)
        title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(title)
        
        # 📄 İÇERİK - GLASSMORPHISM TEXT AREA
        self.info_label = QLabel("Yükleniyor...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Segoe UI', 14))
        self.info_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255, 255, 255, 0.08),
                stop:1 rgba(255, 255, 255, 0.03));
            border-radius: 15px;
            padding: 20px;
            line-height: 1.6;
            border: 1px solid rgba(255, 255, 255, 0.15);
            /* 🌟 CONTENT AREA SHADOWS */
            box-shadow: 
                inset 0 2px 10px rgba(0, 0, 0, 0.1),
                inset 0 -2px 10px rgba(255, 255, 255, 0.05),
                0 5px 15px rgba(0, 0, 0, 0.1);
        """)
        self.info_label.setMinimumHeight(180)
        self.info_label.setMaximumHeight(200)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_container)

    def create_modern_qr_map_section(self, layout):
        """🎯 FLOATING QR + MAP CARDS - ADVANCED GLASSMORPHISM"""
        row_widget = QWidget()
        row_widget.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(20)
        
        # 📱 QR FLOATING CARD
        qr_container = QWidget()
        qr_container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.18),
                stop:0.5 rgba(255, 255, 255, 0.12),
                stop:1 rgba(255, 255, 255, 0.08));
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            /* 🌟 QR CARD FLOATING SHADOWS */
            box-shadow: 
                /* Hover hazır floating effect */
                0 20px 40px rgba(0, 0, 0, 0.25),
                /* Glassmorphism depth */
                inset 0 2px 0 rgba(255, 255, 255, 0.4),
                inset 0 -1px 0 rgba(0, 0, 0, 0.1),
                /* QR specific glow */
                0 0 30px rgba(52, 152, 219, 0.15),
                /* Bottom depth */
                0 25px 50px rgba(0, 0, 0, 0.15);
        """)
        
        qr_layout = QVBoxLayout(qr_container)
        qr_layout.setContentsMargins(20, 20, 20, 20)
        qr_layout.setSpacing(0)
        
        self.qr_label = QLabel("QR\nYükleniyor...")
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(160, 160)
        self.qr_label.setStyleSheet(f"""
            background: {self.colors['white']};
            border-radius: 15px;
            color: {self.colors['dark_gray']};
            font-size: 14px;
            border: 3px solid rgba(255, 215, 0, 0.6);
            /* 🌟 QR CODE INNER SHADOW */
            box-shadow: 
                inset 0 3px 10px rgba(0, 0, 0, 0.1),
                0 0 20px rgba(255, 215, 0, 0.3);
        """)
        
        qr_center_layout = QHBoxLayout()
        qr_center_layout.addStretch()
        qr_center_layout.addWidget(self.qr_label)
        qr_center_layout.addStretch()
        qr_layout.addLayout(qr_center_layout)
        
        row_layout.addWidget(qr_container, 1)
        
        # 🗺️ MAP FLOATING CARD
        map_container = QWidget()
        map_container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255, 255, 255, 0.16),
                stop:0.5 rgba(255, 255, 255, 0.10),
                stop:1 rgba(255, 255, 255, 0.06));
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.25);
            /* 🌟 MAP CARD FLOATING SHADOWS */
            box-shadow: 
                /* Ana floating gölge */
                0 22px 45px rgba(0, 0, 0, 0.28),
                /* Glassmorphism iç efekt */
                inset 0 2px 0 rgba(255, 255, 255, 0.35),
                inset 0 -1px 0 rgba(0, 0, 0, 0.12),
                /* Map specific glow */
                0 0 35px rgba(52, 152, 219, 0.18),
                /* Gradient shadow */
                0 28px 55px rgba(52, 152, 219, 0.12);
        """)
        
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(20, 20, 20, 20)
        map_layout.setSpacing(0)
        
        self.map_label = QLabel("Harita yükleniyor...")
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setMinimumHeight(160)
        self.map_label.setMaximumHeight(180)
        self.map_label.setStyleSheet(f"""
            background: {self.colors['white']};
            border-radius: 15px;
            color: {self.colors['dark_gray']};
            font-size: 14px;
            border: 3px solid rgba(52, 152, 219, 0.4);
            /* 🌟 MAP INNER EFFECTS */
            box-shadow: 
                inset 0 3px 10px rgba(0, 0, 0, 0.08),
                0 0 25px rgba(52, 152, 219, 0.2);
        """)
        map_layout.addWidget(self.map_label)
        
        row_layout.addWidget(map_container, 2)
        layout.addWidget(row_widget)

    def create_modern_footer(self, layout):
        """🌊 FLOATING FOOTER - GLASSMORPHISM"""
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0.12),
                stop:0.5 rgba(255, 255, 255, 0.08),
                stop:1 rgba(255, 255, 255, 0.12));
            border-radius: 20px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            /* 🌟 FOOTER FLOATING SHADOWS */
            box-shadow: 
                /* Subtle floating */
                0 15px 30px rgba(0, 0, 0, 0.2),
                /* Glassmorphism depth */
                inset 0 1px 0 rgba(255, 255, 255, 0.3),
                inset 0 -1px 0 rgba(0, 0, 0, 0.1),
                /* Soft glow */
                0 0 30px rgba(255, 255, 255, 0.1);
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(25, 15, 25, 15)
        
        self.last_update_label = QLabel("Son güncelleme: --:--")
        self.last_update_label.setFont(QFont('Segoe UI', 13))
        self.last_update_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: transparent;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
        """)
        footer_layout.addWidget(self.last_update_label)
        
        footer_layout.addStretch()
        
        status_label = QLabel("● SİSTEM AKTİF")
        status_label.setFont(QFont('Segoe UI', 13, QFont.Bold))
        status_label.setStyleSheet("""
            color: #00ff88;
            background: transparent;
            text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
        """)
        footer_layout.addWidget(status_label)
        
        footer_layout.addStretch()
        
        powered_label = QLabel("✨ Powered by AI")
        powered_label.setFont(QFont('Segoe UI', 11))
        powered_label.setStyleSheet(f"""
            color: {self.colors['white']};
            background: transparent;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
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
                        scaled_logo = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.logo_label.setPixmap(scaled_logo)
                        logo_loaded = True
                        print(f"✅ Logo yüklendi: {path}")
                        break
            if not logo_loaded:
                self.logo_label.setText("🏥")
                self.logo_label.setFont(QFont('Segoe UI', 45))
                print("📋 Logo bulunamadı, emoji kullanıldı")
        except Exception as e:
            self.logo_label.setText("🏥")
            self.logo_label.setFont(QFont('Segoe UI', 45))
            print(f"⚠️ Logo hatası: {e}")

    def update_time(self):
        """Saat güncelle"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        display_text = f"{time_str}\n{date_str}"
        self.time_label.setText(display_text)

    def setup_video_ui(self):
        """Video UI"""
        widget = self.video_widget
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        widget.setStyleSheet(f"background: {self.colors['primary']};")
        
        self.video_widget_display = QVideoWidget()
        layout.addWidget(self.video_widget_display)
        
        self.no_video_label = QLabel("📺 ads/ klasöründe video bulunamadı")
        self.no_video_label.setAlignment(Qt.AlignCenter)
        self.no_video_label.setFont(QFont('Segoe UI', 32, QFont.Bold))
        self.no_video_label.setStyleSheet(f"""
            background: {self.colors['primary']};
            color: {self.colors['white']};
            padding: 50px;
        """)
        self.no_video_label.hide()
        layout.addWidget(self.no_video_label)

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
        """Timer kurulum - NÖBET SAATLERİ İLE"""
        # Eczane bilgileri güncelleme - 30 dakika
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.fetch_data)
        self.update_timer.start(1800000)  # 30 dakika

        # 🕐 NÖBET SAATLERİ KONTROLÜ - HER DAKİKA
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule_and_switch)
        self.schedule_timer.start(60000)  # 60 saniye - dakika kontrolü
        
        print("⏰ Nöbet saatleri kontrolü aktif: 18:45-08:45")

    def check_schedule_and_switch(self):
        """🕐 NÖBET SAATLERİ KONTROLÜ VE MOD DEĞİŞİMİ"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Pazartesi, 6=Pazar
        
        # ⏰ NÖBET SAATLERİ: 18:45 - 08:45 + PAZAR TÜM GÜN
        is_night_shift = (
            current_time >= datetime.strptime("18:45", "%H:%M").time() or
            current_time <= datetime.strptime("08:45", "%H:%M").time()
        )
        
        is_sunday = (current_day == 6)  # Pazar günü
        
        # 🏥 NÖBET ZAMANI KONTROLÜ
        should_show_pharmacy = is_night_shift or is_sunday
        
        if should_show_pharmacy and self.current_mode != "pharmacy":
            print(f"🏥 NÖBET MODUNA GEÇİYOR - Saat: {now.strftime('%H:%M')} {'(PAZAR)' if is_sunday else '(GECE NÖBETİ)'}")
            self.switch_to_pharmacy_mode()
            
        elif not should_show_pharmacy and self.current_mode != "video":
            print(f"🎬 REKLAM MODUNA GEÇİYOR - Saat: {now.strftime('%H:%M')} (NORMAL MESAI)")
            self.switch_to_video_mode()
            
        # Status indicator güncelle
        self.update_status_indicator(should_show_pharmacy, is_sunday)

    def update_status_indicator(self, is_pharmacy_time, is_sunday):
        """🟢 STATUS INDICATOR GÜNCELLE"""
        if hasattr(self, 'status_label'):
            if is_sunday:
                self.status_label.setText("🟢 PAZAR NÖBETÇİSİ")
                self.status_label.setStyleSheet("""
                    color: #00ff88;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 136, 0.2),
                        stop:1 rgba(0, 255, 136, 0.1));
                    border: 2px solid rgba(0, 255, 136, 0.4);
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-weight: bold;
                    text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
                    /* 💚 PULSE ANİMASYON */
                    animation: pulse 2s ease-in-out infinite alternate;
                """)
            elif is_pharmacy_time:
                self.status_label.setText("🟢 ŞU ANDA NÖBETÇİ")
                self.status_label.setStyleSheet("""
                    color: #00ff88;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 255, 136, 0.2),
                        stop:1 rgba(0, 255, 136, 0.1));
                    border: 2px solid rgba(0, 255, 136, 0.4);
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-weight: bold;
                    text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
                """)
            else:
                self.status_label.setText("⚪ REKLAM ZAMANI")
                self.status_label.setStyleSheet("""
                    color: #cccccc;
                    background: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 15px;
                    padding: 8px 15px;
                    font-weight: bold;
                    text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
                """)

    def switch_to_video_mode(self):
        """🎬 Video moduna geç"""
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
            print("❌ Video bulunamadı - ads/ klasörü kontrol edin")

    def switch_to_pharmacy_mode(self):
        """Eczane moduna geç"""
        self.current_mode = "pharmacy"
        if hasattr(self, 'media_player') and self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.stop()
        self.stacked_widget.setCurrentWidget(self.pharmacy_widget)
        self.fetch_data()
        self.fetch_weather_data()

    def fetch_data(self):
        """Gerçek eczane verisi çek"""
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
                    
                    # 🎨 MODERN HTML formatında bilgi - GLASSMORPHISM STYLE
                    info_html = f"""
                    <div style='line-height: 1.8; font-size: 16px;'>
                    <p style='color: {self.colors['gold']}; font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);'>
                    ✨ {name} ✨
                    </p>
                    
                    <div style='background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; margin: 10px 0; border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <p style='color: {self.colors['white']}; margin: 8px 0; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);'>
                    📞 <strong style='color: {self.colors['blue']};'>Tel:</strong> {phone}
                    </p>
                    </div>
                    
                    <div style='background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; margin: 10px 0; border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <p style='color: {self.colors['white']}; margin: 8px 0; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);'>
                    📍 <strong style='color: {self.colors['orange']};'>Adres:</strong><br>{address}
                    </p>
                    </div>
                    
                    <div style='background: rgba(233, 69, 96, 0.1); border-radius: 12px; padding: 15px; margin: 15px 0; border: 2px solid rgba(233, 69, 96, 0.3);'>
                    <p style='color: {self.colors['gold']}; margin: 8px 0; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);'>
                    🚗 <strong>Mesafe:</strong> {distance}
                    </p>
                    <p style='color: {self.colors['gold']}; margin: 8px 0; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);'>
                    ⏱️ <strong>Süre:</strong> {duration}
                    </p>
                    </div>
                    
                    <p style='color: {self.colors['blue']}; text-align: center; font-weight: bold; margin: 15px 0; text-shadow: 0 0 12px rgba(52, 152, 219, 0.4);'>
                    🏢 KARŞIYAKA 4 BÖLGE
                    </p>
                    </div>
                    """
                    
                    self.info_label.setText(info_html)
                    
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
            
            # Bulunamadı - MODERN STYLE
            self.info_label.setText(f"""
            <div style='text-align: center; padding: 30px;'>
            <p style='color: {self.colors['accent']}; font-size: 32px; margin-bottom: 20px; text-shadow: 0 0 20px rgba(233, 69, 96, 0.6);'>⚠️</p>
            <p style='color: {self.colors['white']}; font-size: 18px; text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);'>Bugün KARŞIYAKA 4'te nöbetçi eczane bulunamadı</p>
            <div style='background: rgba(233, 69, 96, 0.1); border-radius: 15px; padding: 20px; margin: 20px 0; border: 2px solid rgba(233, 69, 96, 0.3);'>
            <p style='color: {self.colors['gold']}; font-size: 16px; text-shadow: 0 0 8px rgba(255, 215, 0, 0.4);'>Lütfen daha sonra tekrar kontrol edin</p>
            </div>
            </div>
            """)
            
            now = datetime.now()
            self.last_update_label.setText(f"Son güncelleme: {now.strftime('%H:%M')} (Bulunamadı)")
            
        except Exception as e:
            self.info_label.setText(f"""
            <div style='text-align: center; padding: 30px;'>
            <p style='color: {self.colors['accent']}; font-size: 28px; margin-bottom: 20px; text-shadow: 0 0 15px rgba(233, 69, 96, 0.6);'>❌</p>
            <p style='color: {self.colors['white']}; font-size: 16px; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);'>Hata: {str(e)}</p>
            <div style='background: rgba(233, 69, 96, 0.1); border-radius: 12px; padding: 15px; margin: 15px 0; border: 1px solid rgba(233, 69, 96, 0.3);'>
            <p style='color: {self.colors['gold']}; text-shadow: 0 0 8px rgba(255, 215, 0, 0.4);'>Bağlantı sorunu yaşanıyor</p>
            </div>
            </div>
            """)
            
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
        """🗺️ MODERN Harita oluştur"""
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
                    
                    # Zoom seviyesi
                    distance_value = route['legs'][0]['distance']['value']
                    if distance_value < 1000:
                        zoom_level = 16
                    elif distance_value < 3000:
                        zoom_level = 15
                    else:
                        zoom_level = 14
                    
                    # 🎨 MODERN MAP STYLE - DARK THEME
                    map_width = 480
                    map_height = 160
                    
                    static_map_url = (
                        f"https://maps.googleapis.com/maps/api/staticmap?"
                        f"size={map_width}x{map_height}&"
                        f"maptype=roadmap&"
                        f"style=feature:all|element:geometry|color:0x212121&"
                        f"style=feature:all|element:labels.icon|visibility:off&"
                        f"style=feature:all|element:labels.text.fill|color:0x757575&"
                        f"style=feature:all|element:labels.text.stroke|color:0x212121&"
                        f"style=feature:road|element:geometry|color:0x2c2c2c&"
                        f"style=feature:road|element:geometry.stroke|color:0x212121&"
                        f"style=feature:road|element:labels.text.fill|color:0x9ca5b3&"
                        f"style=feature:water|element:geometry|color:0x17263c&"
                        f"markers=color:0x00ff88|size:mid|label:K|{self.start_lat},{self.start_lon}&"
                        f"markers=color:0xe94560|size:mid|label:E|{end_lat},{end_lon}&"
                        f"path=color:0xffd700|weight:5|enc:{polyline}&"
                        f"zoom={zoom_level}&"
                        f"key={self.api_key}"
                    )
                    
                    # Harita resmini indir
                    map_response = requests.get(static_map_url, timeout=10)
                    
                    if map_response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(map_response.content)
                        
                        scaled_pixmap = pixmap.scaled(480, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.map_label.setPixmap(scaled_pixmap)
                        
                        print("✅ Modern dark theme harita oluşturuldu")
                        return
                        
        except Exception as e:
            print(f"Harita hatası: {e}")
            
        self.map_label.setText("🗺️ Harita yüklenemedi")
        self.map_label.setStyleSheet(f"""
            background: {self.colors['glass']};
            color: {self.colors['white']};
            font-size: 16px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        """)

    def fetch_weather_data(self):
        """🌤️ Hava durumu çek"""
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
            
            self.weather_temp.setText(f"{temp}°C")
            self.weather_desc.setText(desc)
            
            print(f"✅ Hava durumu: {temp}°C - {desc}")
            
        except Exception as e:
            self.weather_temp.setText("--°C")
            self.weather_desc.setText("Hata")
            print(f"Hava durumu hatası: {e}")

    def create_qr_code(self, url):
        """📱 QR kod oluştur"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            # 🎨 MODERN QR DESIGN
            qr_img = qr.make_image(fill_color=self.colors['primary'], back_color=self.colors['white'])
            
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            scaled_pixmap = pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
            print("✅ QR kodu oluşturuldu")
            
        except Exception as e:
            self.qr_label.setText(f"📱\nQR Hatası")
            self.qr_label.setStyleSheet(f"""
                background: {self.colors['glass']};
                color: {self.colors['white']};
                font-size: 14px;
                text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
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
    print("🌟 Modern Glassmorphism Pharmacy Monitor")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    
    # 🎨 MODERN FONT SETUP
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    try:
        window = ElegantVerticalEczaneApp()
        print("✅ Modern glassmorphism pencere oluşturuldu")
        print("📐 Dikey format: 720x1280")
        print("🌟 Advanced shadows & glassmorphism aktif")
        print("🎨 Modern depth effects uygulandı")
        print("⌨️  ESC: Çıkış, F11: Tam ekran")
        print("🔄 30 dakikada otomatik güncelleme")
        print("=" * 70)
        print("🚀 MODERN GLASSMORPHISM ÇALIŞIYOR!")
        
        app.exec_()
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
