# Claude - Nöbetçi Eczane Gösterge Sistemi

Modern ve şık tasarımlı nöbetçi eczane bilgi sistemi. PyQt5 tabanlı bu uygulama, İzmir Eczacı Odası'ndan nöbetçi eczane bilgilerini çekerek arayüzde gösterir.

## 🌟 Özellikler

###
🔥 KARŞIYAKA 4 Eczane Projesi - TAM ÇALIŞIYOR:

GitHub: https://github.com/pelte-kofte/claude
Çalışan dosya: main_final.py

Scraping detayları:
- HTML yapısı: h4.red > strong içinde "KARŞIYAKA 4"
- Google Maps: parent div'de google.com/maps linki
- QR kod: maps URL'sinden oluşturuluyor
- UI: PyQt5 - sol taraf bilgiler, sağ taraf QR kod

Son commit: "Working KARŞIYAKA 4 scraping with QR code"
Status: ✅ FULL WORKING

Çalıştırma:
pip install -r requirements.txt
python main_final.py

###
echo # KARŞIYAKA 4 Nöbetçi Eczane Sistemi > README.md
echo. >> README.md
echo ## Çalıştırma: >> README.md
echo pip install -r requirements.txt >> README.md
echo python main_final.py >> README.md
echo. >> README.md
echo ## Scraping Detayları: >> README.md
echo - HTML yapısı: h4.red ^> strong >> README.md
echo - Google Maps: parent div'de google.com/maps >> README.md
echo - QR kod: maps linkinden oluşur >> README.md
### 🌤️ Hava Durumu
- OpenWeatherMap API entegrasyonu
- İzmir için güncel hava durumu
- Sıcaklığa göre renk kodlaması
- 15 dakikada bir otomatik güncelleme

### 📺 Reklam Sistemi
- Zaman tabanlı ekran değiştirme
- Video reklam desteği (MP4, AVI, MOV, MKV, WebM)
- Otomatik video döngüsü
- Nöbet saatleri dışında reklam gösterimi (8:45-18:45)

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- PyQt5
- İnternet bağlantısı

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
