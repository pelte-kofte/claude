#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude - Configuration Management
Centralized configuration for the pharmacy display system
"""

import os
from PyQt5.QtCore import QTime

class Config:
    """Application configuration class"""
    
    # =====================================
    # API CONFIGURATION
    # =====================================
    
    # Google Maps API Key
    # Get from: https://console.cloud.google.com/
    # Required APIs: Maps Static API, Directions API
    GOOGLE_MAPS_API_KEY = os.getenv(
        "GOOGLE_MAPS_API_KEY", 
        "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
    )
    
    # OpenWeatherMap API Key  
    # Get from: https://openweathermap.org/api
    OPENWEATHER_API_KEY = os.getenv(
        "OPENWEATHER_API_KEY", 
        "b0d1be7721b4967d8feb810424bd9b6f"
    )
    
    # =====================================
    # LOCATION SETTINGS
    # =====================================
    
    # Weather city for OpenWeatherMap
    OPENWEATHER_CITY = "Izmir"
    OPENWEATHER_LANG = "tr"
    OPENWEATHER_UNITS = "metric"
    
    # Home base coordinates (Eczane Kusdemir)
    # Used as starting point for route calculations
    ECZANE_KUSDEMIR_LAT = 38.47422
    ECZANE_KUSDEMIR_LON = 27.11251
    
    # Target region for pharmacy filtering
    # Available regions: KARŞIYAKA 1, KARŞIYAKA 2, KARŞIYAKA 3, KARŞIYAKA 4
    # BORNOVA 1, BORNOVA 2, BUCA 1, BUCA 2, ÇİĞLİ 1, etc.
    TARGET_REGION = "KARŞIYAKA 4"
    
    # =====================================
    # TIMING CONFIGURATION
    # =====================================
    
    # Update intervals (in milliseconds)
    DATA_REFRESH_INTERVAL = 7200000      # 2 hours - Pharmacy data refresh
    TIME_UPDATE_INTERVAL = 1000          # 1 second - Clock update
    WEATHER_UPDATE_INTERVAL = 900000     # 15 minutes - Weather refresh
    DISPLAY_MODE_CHECK_INTERVAL = 120000 # 2 minutes - Screen mode check
    
    # Nöbet (duty) time schedule
    # Format: QTime(hour, minute)
    NOBET_START_TIME = QTime(18, 45)  # 6:45 PM
    NOBET_END_TIME = QTime(8, 45)     # 8:45 AM (next day)
    
    # =====================================
    # UI CONFIGURATION
    # =====================================
    
    # Card styling
    CARD_MARGIN = 25
    CARD_PADDING = 25
    MAP_HEIGHT = 400
    QR_SIZE = 120
    
    # Colors (hex format)
    class Colors:
        # Background colors
        PRIMARY_BG = "#0a0a0a"      # Main background
        SECONDARY_BG = "#1a1a1a"    # Header background
        CARD_BG = "#1e1e1e"         # Card background
        
        # Text colors
        PRIMARY_TEXT = "#ffffff"     # Main text
        SECONDARY_TEXT = "#cccccc"   # Secondary text
        MUTED_TEXT = "#888888"       # Muted text
        
        # Accent colors
        SEPARATOR = "#404040"        # Separator lines
        SHADOW = "#000000"           # Shadow color
        
        # Weather colors (temperature based)
        HOT = "#ff6b6b"             # 30°C+
        WARM = "#ffd93d"            # 20-29°C
        MILD = "#6bcf7f"            # 10-19°C
        COOL = "#4dabf7"            # 0-9°C
        COLD = "#868e96"            # Below 0°C
    
    # Font configuration
    class Fonts:
        FAMILY = "'Inter', 'Segoe UI', 'Roboto', sans-serif"
        TITLE_SIZE = 44
        SUBTITLE_SIZE = 24
        CARD_TITLE_SIZE = 28
        CARD_TEXT_SIZE = 18
        WEATHER_SIZE = 22
        TIME_SIZE = 16
    
    # =====================================
    # NETWORK CONFIGURATION
    # =====================================
    
    # Request timeouts (in seconds)
    WEB_SCRAPE_TIMEOUT = 30
    API_REQUEST_TIMEOUT = 10
    GEOCODING_TIMEOUT = 10
    MAP_REQUEST_TIMEOUT = 15
    
    # Rate limiting delays (in seconds)
    GEOCODING_DELAY = 0.5
    ERROR_RETRY_DELAY = 2
    
    # =====================================
    # DATA SOURCE CONFIGURATION
    # =====================================
    
    # Primary data source URL
    PHARMACY_DATA_URL = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
    
    # User agent for web requests
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Geocoding service configuration
    GEOCODING_USER_AGENT = "eczane_nobet_uygulamasi_vitrin"
    
    # =====================================
    # FILE PATHS
    # =====================================
    
    # Get base directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Asset paths
    LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
    ADS_FOLDER = os.path.join(BASE_DIR, "ads")
    LOG_FILE = os.path.join(BASE_DIR, "eczane_app.log")
    
    # Supported video formats for advertisements
    SUPPORTED_VIDEO_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')
    
    # =====================================
    # DEBUG AND DEVELOPMENT
    # =====================================
    
    # Debug mode (enables extra logging)
    DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
    
    # Test mode (always show pharmacy screen)
    TEST_MODE = os.getenv("TEST_MODE", "True").lower() == "true"
    
    # Enable/disable features
    ENABLE_WEATHER = True
    ENABLE_MAPS = True
    ENABLE_QR_CODES = True
    ENABLE_ADVERTISEMENTS = True
    
    # =====================================
    # LOGGING CONFIGURATION
    # =====================================
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # =====================================
    # VALIDATION METHODS
    # =====================================
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check API keys
        if not cls.GOOGLE_MAPS_API_KEY or cls.GOOGLE_MAPS_API_KEY == "your_api_key_here":
            errors.append("Google Maps API key not configured")
        
        if not cls.OPENWEATHER_API_KEY or cls.OPENWEATHER_API_KEY == "your_api_key_here":
            errors.append("OpenWeatherMap API key not configured")
        
        # Check coordinates
        if not (-90 <= cls.ECZANE_KUSDEMIR_LAT <= 90):
            errors.append("Invalid latitude for Eczane Kusdemir")
        
        if not (-180 <= cls.ECZANE_KUSDEMIR_LON <= 180):
            errors.append("Invalid longitude for Eczane Kusdemir")
        
        # Check directories
        if cls.ENABLE_ADVERTISEMENTS and not os.path.exists(cls.ADS_FOLDER):
            os.makedirs(cls.ADS_FOLDER, exist_ok=True)
        
        return errors
    
    @classmethod
    def get_config_summary(cls):
        """Get configuration summary for logging"""
        return {
            "target_region": cls.TARGET_REGION,
            "weather_city": cls.OPENWEATHER_CITY,
            "test_mode": cls.TEST_MODE,
            "debug_mode": cls.DEBUG_MODE,
            "features": {
                "weather": cls.ENABLE_WEATHER,
                "maps": cls.ENABLE_MAPS,
                "qr_codes": cls.ENABLE_QR_CODES,
                "ads": cls.ENABLE_ADVERTISEMENTS
            }
        }

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG_MODE = True
    TEST_MODE = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG_MODE = False
    TEST_MODE = False
    LOG_LEVEL = "INFO"

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG_MODE = True
    TEST_MODE = True
    DATA_REFRESH_INTERVAL = 60000  # 1 minute for testing
    WEATHER_UPDATE_INTERVAL = 30000  # 30 seconds for testing

# Select configuration based on environment
ENV = os.getenv("ENV", "development").lower()

if ENV == "production":
    config = ProductionConfig
elif ENV == "testing":
    config = TestingConfig
else:
    config = DevelopmentConfig

# Export the selected configuration
Config = config 
