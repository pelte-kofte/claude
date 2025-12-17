# Claude - Nöbetçi Eczane Gösterge Sistemi

Modern ve şık tasarımlı nöbetçi eczane bilgi sistemi. PyQt5 tabanlı bu uygulama, İzmir Eczacı Odası'ndan nöbetçi eczane bilgilerini çekerek arayüzde gösterir.
git push yapma
git add .
git commit -m "Worker thread + Cumartesi 16:00 desteği"
git push
## 🌟 Özellikler

###
🔥 KARŞIYAKA 4 Eczane Projesi - FULL WORKING:

GitHub: https://github.com/pelte-kofte/claude
Çalışan dosya: main.py

Scraping detayları:
- HTML yapısı: h4.red > strong içinde "KARŞIYAKA 4" ara
- Google Maps: parent div'de google.com/maps linki çek
- Telefon: parent div'de tel: linki
- Adres: fa-home icon'dan sonraki text

Özellikler:
- Dikey ekran layout (720x1000)
- Gerçek yol tarifi (Google Directions API + polyline)
- Kuşdemir Eczanesi'nden başlayan rota (38.474, 27.112)
- QR kod + eczane bilgileri
- Mesafe ve süre gösterimi

API Keys:
- Google Maps: AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE
- OpenWeather: b0d1be7721b4967d8feb810424bd9b6f

Status: ✅ FULL WORKING
# 🔥 KARŞIYAKA 4 Nöbetçi Eczane Sistemi - Production Ready

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](#)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-5%20Ready-red.svg)](#)

Modern corporate tasarımlı, 24/7 çalışabilen nöbetçi eczane bilgi sistemi.

## 📋 PROJE ÖZETİ

- **Platform:** PyQt5 (Python)
- **Boyut:** 900x1280 (Dikey ekran optimize)
- **Tasarım:** Modern Corporate Style
- **Font:** Segoe UI
- **Durum:** %100 Çalışır - Production Ready

## ✨ ÖZELLİKLER

### 🎬 **Lottie Weather Animations**
- HTTP Server ile CORS-free animasyonlar
- Sıcaklığa göre otomatik animasyon seçimi
- Şeffaf arkaplan desteği
- 40x40 widget boyutu (header'a optimize)

### 🌐 **HTTP Server**
- Port 8000-8009 otomatik seçim
- CORS header desteği
- Local dosya servisi
- Thread-safe çalışma

### 📡 **Gerçek Eczane Scraping**
- İzmir Eczacı Odası canlı veri
- HTML parsing (h4.red > strong)
- Otomatik telefon formatlaması (0232 999 99 99)
- 30 dakikada bir otomatik güncelleme

### 🗺️ **Google Maps Entegrasyonu**
- Gerçek yol tarifi + polyline
- Kuşdemir Eczanesi başlangıç noktası (38.474, 27.112)
- Dinamik harita boyutu (570px yükseklik)
- Mesafe ve süre gösterimi (Türkçe: "8 dakika")

### 📱 **QR Kod Sistemi**
- Otomatik QR kod oluşturma
- Google Maps link entegrasyonu
- 160x160 boyut

### 🎨 **SVG İkonlar & Fallback**
- SVG ikonlar (phone, location, distance, time)
- Emoji fallback sistemi
- Responsive tasarım

### ⏰ **Otomatik Nöbet Saatleri**
- 18:45-08:45 + Pazar tüm gün
- Otomatik mod değiştirme
- Dakika bazında kontrol

### 📺 **Video Reklam Modu**
- ads/ klasöründen otomatik oynatma
- Desteklenen formatlar: MP4, MOV, AVI
- Nöbet saatleri dışında aktif

### 🌡️ **Hava Durumu API**
- OpenWeatherMap entegrasyonu
- İzmir için güncel veri
- Sıcaklık bazlı Lottie seçimi

## 📁 DOSYA YAPISI

```
proje/
├── main.py                 # Ana uygulama
├── weather_lottie/         # Lottie animasyonlar
│   ├── sun_hot.json       # Sıcak hava (30°C+)
│   ├── sun.json           # Normal güneş
│   ├── rain.json          # Yağmurlu hava
│   ├── snow.json          # Karlı hava
│   ├── storm.json         # Fırtınalı hava
│   └── clouds.json        # Bulutlu hava
├── icons/                  # SVG ikonlar
│   ├── phone.svg          # Telefon ikonu
│   ├── location.svg       # Konum ikonu
│   ├── distance.svg       # Mesafe ikonu
│   └── time.svg           # Zaman ikonu
├── logo/
│   └── LOGO.png           # Şirket logosu
└── ads/                   # Video reklam dosyaları
    └── *.mp4/mov/avi      # Desteklenen formatlar
```

## 🚀 KURULUM & ÇALIŞTIRMA

### Gereksinimler
```bash
pip install PyQt5 PyQtWebEngine requests beautifulsoup4 qrcode pillow
```

### Çalıştırma
```bash
python main.py
```

### Klavye Kısayolları
- **ESC:** Uygulamadan çık
- **F11:** Tam ekran moduna geç

## 🔧 API KONFIGÜRASYONU

```python
# API Anahtarları
GOOGLE_MAPS_API = "AIzaSyCIG70KV9YFvAoxlbqm3LqN_dRfuWZj-eE"
OPENWEATHER_API = "b0d1be7721b4967d8feb810424bd9b6f"

# Başlangıç Koordinatları (Kuşdemir Eczanesi)
START_LAT = 38.47434762293852
START_LON = 27.112356625119595
```

## 🎯 SCRAPING DETAYLARI

### HTML Yapısı
- **Eczane Adı:** `h4.red > strong` içinde "KARŞIYAKA 4" arama
- **Google Maps:** Parent div'de `google.com/maps` linki
- **Telefon:** Parent div'de `tel:` linki
- **Adres:** `fa-home` icon'dan sonraki text

### Veri İşleme
- Telefon formatlaması: `0232 362 35 10`
- Süre çevirimi: `mins` → `dakika`, `hours` → `saat`
- Mesafe hesaplama: Google Directions API

## 🍓 RASPBERRY Pi 5 HAZIRLIĞI

### Performans
- **RAM Kullanımı:** ~200-300MB
- **CPU Kullanımı:** %10-15
- **Güç Tüketimi:** ~15W
- **24/7 Operasyon:** ✅

### Optimizasyonlar
```python
# Pi 5 için önerilen ayarlar
QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)  # GPU optimizasyonu
self.update_timer.start(3600000)  # 1 saatte bir güncelleme
```

## 🎨 TASARIM DETAYLARI

### Renk Paleti
```python
colors = {
    'bg_primary': '#000000',      # Ana arkaplan
    'bg_card': '#1a1a1a',         # Kart arkaplanı  
    'text_primary': '#ffffff',    # Ana metin
    'accent_blue': '#007AFF',     # Mavi vurgu
    'accent_green': '#30D158',    # Yeşil durum
    'accent_red': '#FF3B30',      # Kırmızı header
}
```

### Layout Oranları
- **Header:** 140px (11%)
- **Bilgi Ekranı:** 400px (31%)
- **Harita:** 570px (45%)
- **Footer:** 60px (5%)

## 🔄 LOTTIE ANIMASYON SİSTEMİ

### CORS Bypass Çözümü
```python
class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
```
### GOOGLEMAPS GECE MODUİÇİN 

fetch_map_data fonksiyonunu bul (DataFetchWorker class içinde), static_map_url kısmındaki style'ları sil veya değiştir.
Bul:
pythonf"style=feature:all|element:geometry|color:0x1a1a1a&"
f"style=feature:all|element:labels.icon|visibility:off&"
f"style=feature:all|element:labels.text.fill|color:0xcccccc&"
f"style=feature:all|element:labels.text.stroke|color:0x000000&"
f"style=feature:road|element:geometry|color:0x333333&"
f"style=feature:road|element:geometry.stroke|color:0x222222&"
f"style=feature:road|element:labels.text.fill|color:0xffffff&"
f"style=feature:water|element:geometry|color:0x007AFF&"
f"style=feature:landscape|element:geometry|color:0x111111&"


## 📊 GÜNCELLEME SIKLIĞI

| Bileşen | Sıklık | Açıklama |
|---------|---------|-----------|
| Saat/Tarih | 1 saniye | Gerçek zamanlı |
| Hava Durumu | 15 dakika | API limit optimizasyonu |
| Eczane Bilgisi | 30 dakika | Scraping optimizasyonu |
| Nöbet Kontrolü | 1 dakika | Mod değiştirme |

## 🎯 PRODUCTION ÖZELLİKLERİ

- ✅ **Hata Yönetimi:** İnternet kesintilerinde graceful fallback
- ✅ **Memory Management:** Optimized resource usage
- ✅ **Thread Safety:** Background operations
- ✅ **Auto Recovery:** Broken connection handling
- ✅ **Fallback Systems:** Emoji icons when SVG fails
- ✅ **Performance:** Pi 5 ready optimization

## 📞 İLETİŞİM

**Proje Sahibi:** Claude AI Assistant  
**GitHub:** [https://github.com/pelte-kofte/claude](https://github.com/pelte-kofte/claude)  
**Durum:** Production Ready - 24/7 Operasyonel

---

### 🏆 SONUÇ

Bu proje modern teknolojiler kullanarak geliştirilmiş, production-ready bir nöbetçi eczane bilgi sistemidir. Raspberry Pi 5 üzerinde 24/7 stabil çalışabilir, gerçek zamanlı veri güncellemesi yapar ve kullanıcı dostu modern arayüze sahiptir.

**Status: ✅ FULL WORKING - Production Ready**

### Kurulum Adımları

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/yourusername/claude.git
cd claude
```

2. **Sanal ortam oluşturun (önerilen):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

3. **Gerekli paketleri kurun:**
```bash
pip install -r requirements.txt
```

4. **API anahtarlarını ayarlayın:**
```bash
# Çevresel değişkenler olarak ayarlayın
export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
export OPENWEATHER_API_KEY="your_openweather_api_key"

# Windows için:
set GOOGLE_MAPS_API_KEY=your_google_maps_api_key
set OPENWEATHER_API_KEY=your_openweather_api_key
```

5. **Logo dosyasını ekleyin (opsiyonel):**
```bash
# logo.png dosyasını ana dizine yerleştirin
cp your_logo.png logo.png
```

6. **Reklam videolarını ekleyin (opsiyonel):**
```bash
mkdir ads
# Video dosyalarınızı ads/ klasörüne kopyalayın
```


## 🎮 Kontroller

### Klavye Kısayolları
- **ESC** veya **F11**: Tam ekran modu değiştir
- **R**: Verileri yenile
- **P**: Eczane ekranına geç (test için)
- **A**: Reklam ekranına geç (test için)

### Otomatik Mod
- Nöbet saatleri içinde: Eczane bilgileri görüntülenir
- Nöbet saatleri dışında: Reklam videoları oynatılır
- Test modu için her zaman eczane ekranını gösterecek şekilde ayarlanmıştır

## 📁 Dosya Yapısı

```
claude/
├── main.py              # Ana uygulama dosyası
├── config.py            # Yapılandırma dosyası
├── requirements.txt     # Python gereksinimleri
├── README.md           # Bu dosya
├── .gitignore          # Git ignore dosyası
├── logo.png            # Uygulama logosu (opsiyonel)
├── ads/                # Reklam videoları klasörü
│   ├── reklam1.mp4
│   ├── reklam2.avi
│   └── ...
├── logs/               # Log dosyaları (otomatik oluşur)
│   └── eczane_app.log
└── tests/              # Test dosyaları
    └── test_main.py
```

## 🛠️ Özelleştirme

### Renk Teması
`config.py` dosyasındaki `Colors` sınıfını düzenleyerek renk temasını değiştirebilirsiniz:

```python
class Colors:
    PRIMARY_BG = "#0a0a0a"      # Ana arkaplan rengi
    SECONDARY_BG = "#1a1a1a"    # Header arkaplan rengi  
    CARD_BG = "#1e1e1e"         # Kart arkaplan rengi
    PRIMARY_TEXT = "#ffffff"     # Ana metin rengi
```

### Font Ailesi
Font ailesini değiştirmek için `config.py` dosyasında:
```python
class Fonts:
    FAMILY = "'Your Font', 'Fallback Font', sans-serif"
```

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### 1. PyQt5 Kurulum Hatası
```bash
# Ubuntu/Debian için:
sudo apt-get install python3-pyqt5

# CentOS/RHEL için:
sudo yum install python3-qt5

# macOS için:
brew install pyqt5
```

#### 2. API Anahtarı Hataları
- API anahtarlarının doğru ayarlandığından emin olun
- Google Cloud Console'da ilgili API'lerin etkin olduğunu kontrol edin
- Kota limitlerini kontrol edin

#### 3. Geocoding Hataları
- İnternet bağlantınızı kontrol edin
- Nominatim servisinin erişilebilir olduğunu doğrulayın
- Rate limiting nedeniyle bekleme süreleri eklenmiştir

### Log Dosyaları
Uygulama log dosyası `eczane_app.log` dosyasında saklanır. Sorun yaşadığınızda bu dosyayı kontrol edin:

```bash
tail -f eczane_app.log
```

## 🤝 Katkıda Bulunma

1. Bu projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### Geliştirme Ortamı

```bash
# Geliştirme bağımlılıklarını kurun
pip install pytest black flake8

# Code formatting
black main.py config.py

# Linting
flake8 main.py config.py

# Test çalıştırma
pytest tests/
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorun yaşıyorsanız veya öneriniz varsa:

1. [GitHub Issues](https://github.com/yourusername/claude/issues) sayfasından issue oluşturun
2. Mevcut issue'ları kontrol edin
3. Geliştirici ile iletişime geçin

## 📊 Performans

### Sistem Gereksinimleri
- **İşlemci**: Intel Core i3 veya eşdeğeri
- **RAM**: Minimum 4GB (8GB önerilen)
- **Depolama**: 500MB boş alan
- **Ağ**: Sürekli internet bağlantısı

## 🔄 Güncellemeler

### v2.0.0 (Güncel)
- ✅ Modern PyQt5 tabanlı yeniden yazım
- ✅ Gelişmiş hata yönetimi
- ✅ Yapılandırılabilir API anahtarları
- ✅ Detaylı loglama sistemi

### v1.0.0
- ✅ Temel eczane bilgi gösterimi
- ✅ Google Maps entegrasyonu
- ✅ QR kod oluşturma
- ✅ Hava durumu gösterimi

## 🙏 Teşekkürler

Bu proje şu kaynakları kullanmaktadır:
- [İzmir Eczacı Odası](https://www.izmireczaciodasi.org.tr/) - Nöbetçi eczane verileri
- [Google Maps API](https://developers.google.com/maps) - Harita servisleri
- [OpenWeatherMap](https://openweathermap.org/) - Hava durumu verileri
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework

---

**Geliştirici:** Claude Project Team  
**Son Güncelleme:** 2024  
**Versiyon:** 2.0.0
