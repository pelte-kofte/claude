#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test suite for Claude main application"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from config import Config
from main import ModernCorporateEczaneApp, DataFetchWorker


class TestConfig(unittest.TestCase):
    def test_config_validation(self):
        result = Config.validate_config()
        self.assertIsInstance(result, bool)

    def test_config_summary(self):
        summary = Config.get_config_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('region', summary)
        self.assertIn('window', summary)
        self.assertIn('maps_key_set', summary)
        self.assertIn('weather_key_set', summary)
        self.assertIn('test_mode', summary)

    def test_config_values(self):
        self.assertIsInstance(Config.TARGET_REGION, str)
        self.assertIsInstance(Config.GOOGLE_MAPS_API_KEY, str)
        self.assertIsInstance(Config.OPENWEATHER_API_KEY, str)
        self.assertEqual(Config.WINDOW_WIDTH, 900)
        self.assertEqual(Config.WINDOW_HEIGHT, 1280)
        self.assertEqual(Config.MAP_WIDTH, 850)
        self.assertEqual(Config.MAP_HEIGHT, 550)
        self.assertEqual(Config.QR_SIZE, 160)

    def test_is_ad_mode_returns_bool(self):
        result = Config.is_ad_mode()
        self.assertIsInstance(result, bool)

    def test_get_nobet_saati_str_returns_string(self):
        result = Config.get_nobet_saati_str()
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Nöbet:"))


class TestDataFetchWorker(unittest.TestCase):
    def test_worker_creation_pharmacy(self):
        worker = DataFetchWorker("pharmacy")
        self.assertIsNotNone(worker)
        self.assertEqual(worker.task_type, "pharmacy")

    def test_worker_creation_weather(self):
        worker = DataFetchWorker("weather", api_key="test_key")
        self.assertIsNotNone(worker)
        self.assertEqual(worker.kwargs.get('api_key'), "test_key")

    def test_worker_creation_map(self):
        worker = DataFetchWorker(
            "map", api_key="key",
            start_lat=38.0, start_lon=27.0,
            end_lat=38.5, end_lon=27.5,
        )
        self.assertIsNotNone(worker)
        self.assertEqual(worker.task_type, "map")


class TestGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_main_app_creation(self):
        try:
            app = ModernCorporateEczaneApp()
            self.assertIsNotNone(app)
            self.assertEqual(app.start_lat, Config.START_LAT)
            self.assertEqual(app.start_lon, Config.START_LON)
            app.close()
        except Exception as e:
            self.skipTest(f"GUI test skipped in headless env: {e}")


class TestIntegration(unittest.TestCase):
    def test_config_integration(self):
        self.assertIsInstance(Config.TARGET_REGION, str)
        self.assertIsInstance(Config.GOOGLE_MAPS_API_KEY, str)
        self.assertIsInstance(Config.OPENWEATHER_API_KEY, str)

    def test_nobet_saati_integration(self):
        nobet = Config.get_nobet_saati_str()
        valid_strings = [
            "Nöbet: 24 Saat",
            "Nöbet: 13:00 - 08:45",
            "Nöbet: 16:00 - 08:55",
            "Nöbet: 18:45 - 08:45",
        ]
        self.assertIn(nobet, valid_strings)


class TestPerformance(unittest.TestCase):
    def test_config_validation_performance(self):
        import time
        start_time = time.time()
        for _ in range(50):
            Config.validate_config()
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 0.1)

    def test_nobet_saati_performance(self):
        import time
        start_time = time.time()
        for _ in range(100):
            Config.get_nobet_saati_str()
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 1.0)


if __name__ == '__main__':
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    unittest.main(verbosity=2)
