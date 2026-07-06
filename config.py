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

    # Harita ayarları (dikey ekran için)
    MAP_WIDTH = 850
    MAP_HEIGHT = 650

    # QR kod ve slayt ayarları
    QR_SIZE = 160
    SLIDE_DURATION = 15000

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
            if gun == 5:
                return "Nöbet: 13:00 - 08:55"
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
