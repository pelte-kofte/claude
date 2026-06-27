import os
from PyQt5.QtCore import QTime
from PyQt5.QtGui import QFont

class Config:
    # API Keys - Environment variable'dan oku
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY", "")
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_KEY") or os.environ.get("OPENWEATHER_API_KEY", "")

    # Bölge ayarları
    TARGET_REGION = "KARŞIYAKA 4"
    CITY_NAME = "İzmir"

    # Dikey ekran boyutları (Portrait Mode)
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 1280

    # Başlangıç koordinatları (Eczanenin konumu)
    START_LAT = 38.47434762293852
    START_LON = 27.112356625119595
    DEFAULT_END_LAT = 38.473137
    DEFAULT_END_LON = 27.113438

    # Raspberry Pi ekran ayarları
    FULLSCREEN = True
    HIDE_CURSOR = True

    # Mod geçiş saatleri
    AD_WEEKDAY_START = QTime(8, 45)
    AD_WEEKDAY_END   = QTime(18, 45)
    AD_SATURDAY_START = QTime(8, 55)
    AD_SATURDAY_END   = QTime(16, 0)

    # Güncelleme aralıkları (milisaniye)
    PHARMACY_UPDATE_INTERVAL = 2 * 60 * 60 * 1000  # 2 saat
    WEATHER_UPDATE_INTERVAL = 15 * 60 * 1000        # 15 dakika
    TIME_UPDATE_INTERVAL = 1000                      # 1 saniye
    MODE_CHECK_INTERVAL = 30_000                     # 30 saniye

    # Test modu (False yaparak normal çalışma moduna geçer)
    TEST_MODE = False

    # Log ayarları
    LOG_LEVEL = "INFO"
    LOG_FILE = "eczane_app.log"

    # Raspberry Pi özel ayarları
    RASPBERRY_PI_MODE = True
    AUTO_START_DELAY = 5  # Sistem başladıktan sonra 5 saniye bekle

    # Koordinat bilgileri (Karşıyaka merkez noktası)
    DEFAULT_LAT = 38.4612
    DEFAULT_LON = 27.1285

    # Harita ayarları (dikey ekran için)
    MAP_WIDTH = 850
    MAP_HEIGHT = 550
    MAP_ZOOM = 14

    # QR kod ayarları
    QR_SIZE = 160

    @classmethod
    def is_ad_mode(cls) -> bool:
        from datetime import datetime
        now = datetime.now()
        gun = now.weekday()
        ay = now.month
        gun_no = now.day
        yil = now.year
        saat = QTime(now.hour, now.minute)
        if cls.TEST_MODE:
            return False
        if gun == 6:
            return False
        RESMI = [(1,1),(4,23),(5,1),(5,19),(7,15),(8,30),(10,29)]
        if (ay, gun_no) in RESMI:
            return False
        BAYRAM = {
            2025:[(3,30),(3,31),(4,1),(6,6),(6,7),(6,8),(6,9)],
            2026:[(3,20),(3,21),(3,22),(5,27),(5,28),(5,29),(5,30)],
            2027:[(3,10),(3,11),(3,12),(5,16),(5,17),(5,18),(5,19)],
        }
        if yil in BAYRAM and (ay, gun_no) in BAYRAM[yil]:
            return False
        AREFE = {2025:[(3,29),(6,5)],2026:[(3,19),(5,26)],2027:[(3,9),(5,15)]}
        SABIT_AREFE = [(10,28),(12,31)]
        is_arefe = (yil in AREFE and (ay, gun_no) in AREFE[yil]) or (ay, gun_no) in SABIT_AREFE
        if is_arefe:
            start = cls.AD_SATURDAY_START if gun == 5 else cls.AD_WEEKDAY_START
            return start <= saat < QTime(13, 0)
        if gun == 5:
            return cls.AD_SATURDAY_START <= saat < cls.AD_SATURDAY_END
        return cls.AD_WEEKDAY_START <= saat < cls.AD_WEEKDAY_END

    @classmethod
    def get_nobet_saati_str(cls) -> str:
        from datetime import datetime
        now = datetime.now()
        gun = now.weekday()
        ay = now.month
        gun_no = now.day
        yil = now.year
        if gun == 6:
            return "Nöbet: 24 Saat"
        RESMI = [(1,1),(4,23),(5,1),(5,19),(7,15),(8,30),(10,29)]
        if (ay, gun_no) in RESMI:
            return "Nöbet: 24 Saat"
        BAYRAM = {
            2025:[(3,30),(3,31),(4,1),(6,6),(6,7),(6,8),(6,9)],
            2026:[(3,20),(3,21),(3,22),(5,27),(5,28),(5,29),(5,30)],
            2027:[(3,10),(3,11),(3,12),(5,16),(5,17),(5,18),(5,19)],
        }
        if yil in BAYRAM and (ay, gun_no) in BAYRAM[yil]:
            return "Nöbet: 24 Saat"
        AREFE = {2025:[(3,29),(6,5)],2026:[(3,19),(5,26)],2027:[(3,9),(5,15)]}
        if (yil in AREFE and (ay, gun_no) in AREFE[yil]) or (ay, gun_no) in [(10,28),(12,31)]:
            return "Nöbet: 13:00 - 08:45"
        if gun == 5:
            return "Nöbet: 16:00 - 08:55"
        return "Nöbet: 18:45 - 08:45"

    @classmethod
    def validate_config(cls) -> bool:
        return bool(cls.GOOGLE_MAPS_API_KEY and cls.OPENWEATHER_API_KEY)

    @classmethod
    def get_config_summary(cls) -> dict:
        return {
            "region": cls.TARGET_REGION,
            "window": f"{cls.WINDOW_WIDTH}x{cls.WINDOW_HEIGHT}",
            "maps_key_set": bool(cls.GOOGLE_MAPS_API_KEY),
            "weather_key_set": bool(cls.OPENWEATHER_API_KEY),
            "test_mode": cls.TEST_MODE,
        }


class Colors:
    # Koyu tema renkler
    PRIMARY_BG = "#0a0a0a"
    SECONDARY_BG = "#1a1a1a"
    CARD_BG = "#1e1e1e"
    ACCENT_BG = "#2a2a2a"

    # Metin renkleri
    PRIMARY_TEXT = "#ffffff"
    SECONDARY_TEXT = "#cccccc"
    ACCENT_TEXT = "#4CAF50"
    WARNING_TEXT = "#FF9800"
    ERROR_TEXT = "#F44336"

    # Sıcaklık renkleri
    TEMP_COLD = "#64B5F6"     # Mavi (soğuk)
    TEMP_MILD = "#81C784"     # Yeşil (ılık)
    TEMP_WARM = "#FFB74D"     # Turuncu (sıcak)
    TEMP_HOT = "#E57373"      # Kırmızı (çok sıcak)

    # Kenar renkleri
    BORDER_COLOR = "#333333"
    SHADOW_COLOR = "#000000"

class Fonts:
    # Dikey ekran için optimize edilmiş font boyutları
    FAMILY = "'Segoe UI', 'Ubuntu', 'Arial', sans-serif"

    # Ana başlık
    TITLE_SIZE = 32
    TITLE_WEIGHT = QFont.Bold

    # Alt başlıklar
    SUBTITLE_SIZE = 24
    SUBTITLE_WEIGHT = QFont.Medium

    # Normal metin
    NORMAL_SIZE = 18
    NORMAL_WEIGHT = QFont.Normal

    # Küçük metin
    SMALL_SIZE = 14
    SMALL_WEIGHT = QFont.Normal

    # Çok küçük metin
    TINY_SIZE = 12
    TINY_WEIGHT = QFont.Light

    # Zaman görünümü
    TIME_SIZE = 28
    TIME_WEIGHT = QFont.Bold

    # Sıcaklık
    TEMP_SIZE = 24
    TEMP_WEIGHT = QFont.Medium

class Styles:
    # Ana pencere stili
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {Colors.PRIMARY_BG};
            color: {Colors.PRIMARY_TEXT};
            font-family: {Fonts.FAMILY};
        }}
    """

    # Header stili (dikey ekran için)
    HEADER = f"""
        QWidget#header {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {Colors.SECONDARY_BG}, stop: 1 {Colors.ACCENT_BG});
            border-bottom: 2px solid {Colors.BORDER_COLOR};
            min-height: 120px;
            max-height: 120px;
        }}
    """

    # Kart stili (dikey ekran için optimize)
    CARD = f"""
        QWidget.card {{
            background-color: {Colors.CARD_BG};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: 12px;
            margin: 8px;
            padding: 12px;
        }}
        QWidget.card:hover {{
            background-color: {Colors.ACCENT_BG};
            border: 1px solid {Colors.ACCENT_TEXT};
        }}
    """

    # Label stilleri
    TITLE_LABEL = f"""
        QLabel {{
            color: {Colors.PRIMARY_TEXT};
            font-size: {Fonts.TITLE_SIZE}px;
            font-weight: bold;
            padding: 8px;
        }}
    """

    SUBTITLE_LABEL = f"""
        QLabel {{
            color: {Colors.ACCENT_TEXT};
            font-size: {Fonts.SUBTITLE_SIZE}px;
            font-weight: 500;
            padding: 4px;
        }}
    """

    NORMAL_LABEL = f"""
        QLabel {{
            color: {Colors.SECONDARY_TEXT};
            font-size: {Fonts.NORMAL_SIZE}px;
            padding: 2px;
            line-height: 1.4;
        }}
    """

    # Scrollbar (dikey ekran için ince)
    SCROLLBAR = f"""
        QScrollBar:vertical {{
            background-color: {Colors.SECONDARY_BG};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {Colors.ACCENT_TEXT};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {Colors.PRIMARY_TEXT};
        }}
    """

class RaspberryPiConfig:
    # GPIO pin'leri (eğer LED/buzzer vs eklenirse)
    STATUS_LED_PIN = 18
    BUZZER_PIN = 24

    # Ekran ayarları
    DISPLAY_ROTATION = 0  # 0, 90, 180, 270
    BRIGHTNESS = 255      # 0-255 arası

    # Güç yönetimi
    SCREEN_SAVER_TIMEOUT = 0  # 0 = kapalı, dakika cinsinden
    AUTO_SHUTDOWN_HOUR = None  # None = kapalı, saat cinsinden

    # Ağ ayarları
    WIFI_CHECK_INTERVAL = 30  # saniye
    OFFLINE_MODE_TIMEOUT = 300  # 5 dakika offline sonra yerel gösterim

    # Sistem kaynak kullanımı
    MAX_CPU_USAGE = 80    # %
    MAX_MEMORY_USAGE = 85 # %

    # Otomatik başlatma
    SERVICE_NAME = "eczane-nobetci"
    SERVICE_DESCRIPTION = "Nöbetçi Eczane Gösterge Sistemi"


# Raspberry Pi için sistem kontrolü
def is_raspberry_pi():
    """Raspberry Pi üzerinde çalışıp çalışmadığını kontrol eder"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
    except:
        return False


# Test ortamı kontrolü
def is_test_environment():
    """Test ortamında çalışıp çalışmadığını kontrol eder"""
    return not is_raspberry_pi() or Config.TEST_MODE
