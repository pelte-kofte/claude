#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EczaneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude - Nöbetçi Eczane Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Ana başlık
        title = QLabel("Claude - Nöbetçi Eczane Sistemi")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setStyleSheet("color: white; background: #1a1a1a; padding: 50px;")
        layout.addWidget(title)
        
        # Alt başlık
        subtitle = QLabel("Sistem başarıyla çalışıyor!\nESC tuşu ile çıkış yapabilirsiniz.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setStyleSheet("color: #cccccc; background: #0a0a0a; padding: 30px;")
        layout.addWidget(subtitle)
        
        # Ana stil
        self.setStyleSheet("QMainWindow { background: #0a0a0a; }")
        
        print("Claude Eczane Sistemi başlatıldı!")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

def main():
    app = QApplication(sys.argv)
    
    try:
        window = EczaneApp()
        window.show()
        print("Pencere açıldı. ESC ile kapatabilirsiniz.")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main() 
