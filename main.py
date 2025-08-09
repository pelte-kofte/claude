import sys
import requests
from bs4 import BeautifulSoup
import qrcode
from io import BytesIO
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class EczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KARŞIYAKA 4 Nöbetçi Eczane")
        self.resize(720, 1000)
        self.setup_ui()
        self.fetch_data()
    
    def setup_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        # Başlık
        title = QLabel("🏥 KARŞIYAKA 4 NÖBETÇİ ECZANE")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Ana içerik - Horizontal layout
        content_layout = QHBoxLayout()
        
        # Sol: Eczane bilgileri
        self.info_label = QLabel("Yükleniyor...")
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont('Arial', 14))
        content_layout.addWidget(self.info_label, 2)
        
        # Sağ: QR kod
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setFixedSize(200, 200)
        content_layout.addWidget(self.qr_label, 1)
        
        layout.addLayout(content_layout)
    
    def fetch_data(self):
        try:
            url = "https://www.izmireczaciodasi.org.tr/nobetci-eczaneler"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            h4_elements = soup.find_all('h4', class_='red')
            
            for h4 in h4_elements:
                strong = h4.find('strong')
                if strong and 'KARŞIYAKA 4' in strong.text.upper():
                    name = strong.text.strip()
                    
                    parent_div = h4.parent
                    
                    # Telefon bul
                    phone = "Bulunamadı"
                    phone_link = parent_div.find('a', href=lambda x: x and 'tel:' in x)
                    if phone_link:
                        phone = phone_link.get('href').replace('tel:', '')
                        if len(phone) == 10:
                            phone = '0' + phone
                    
                    # Google Maps linki bul
                    maps_link = parent_div.find('a', href=lambda x: x and 'google.com/maps' in x)
                    maps_url = maps_link.get('href') if maps_link else None
                    
                    # Bilgileri göster
                    info_text = f"✅ {name}\n\n📞 {phone}\n\n🏢 KARŞIYAKA 4"
                    if maps_url:
                        info_text += f"\n\n🗺️ Harita mevcut"
                    
                    self.info_label.setText(info_text)
                    
                    # QR kod oluştur ve göster
                    if maps_url:
                        self.create_qr_code(maps_url)
                    
                    return
            
            self.info_label.setText("❌ Bugün KARŞIYAKA 4'te nöbetçi eczane bulunamadı")
            
        except Exception as e:
            self.info_label.setText(f"❌ Hata: {str(e)}")
    
    def create_qr_code(self, url):
        try:
            # QR kod oluştur
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color='black', back_color='white')
            
            # PIL'den QPixmap'e çevir
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            # QR label'a koy
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.qr_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.qr_label.setText(f"QR Hatası: {str(e)}")

app = QApplication(sys.argv)
window = EczaneApp()
window.show()
app.exec_()
