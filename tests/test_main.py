 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Claude main application
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Qt test framework
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Import application modules
from main import (
    Config, PharmacyData, GeoUtils, GeoCoder, PharmacyScraper,
    WeatherService, CircularQLabel, PharmacyScreen, AdScreen, EczaneApp
)

class TestConfig(unittest.TestCase):
    """Test configuration class"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        errors = Config.validate_config()
        # Should return a list (empty or with errors)
        self.assertIsInstance(errors, list)
    
    def test_config_summary(self):
        """Test configuration summary generation"""
        summary = Config.get_config_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('target_region', summary)
        self.assertIn('features', summary)

class TestPharmacyData(unittest.TestCase):
    """Test pharmacy data model"""
    
    def setUp(self):
        self.pharmacy = PharmacyData(
            name="Test Eczane",
            address="Test Adres 123",
            phone="0232 123 4567",
            region="KARŞIYAKA 4",
            map_url="https://maps.google.com/test",
            coordinates={"lat": 38.123, "lon": 27.456}
        )
    
    def test_pharmacy_creation(self):
        """Test pharmacy data creation"""
        self.assertEqual(self.pharmacy.name, "Test Eczane")
        self.assertEqual(self.pharmacy.region, "KARŞIYAKA 4")
        self.assertIsInstance(self.pharmacy.coordinates, dict)
    
    def test_pharmacy_to_dict(self):
        """Test pharmacy data serialization"""
        data = self.pharmacy.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['name'], "Test Eczane")
        self.assertIn('coordinates', data)

class TestGeoUtils(unittest.TestCase):
    """Test geographical utility functions"""
    
    def test_extract_coords_from_map_url_q_pattern(self):
        """Test coordinate extraction from Google Maps URL with ?q= pattern"""
        url = "https://maps.google.com/?q=38.4742,27.1125"
        lat, lon = GeoUtils.extract_coords_from_map_url(url)
        self.assertEqual(lat, 38.4742)
        self.assertEqual(lon, 27.1125)
    
    def test_extract_coords_from_map_url_at_pattern(self):
        """Test coordinate extraction from Google Maps URL with @ pattern"""
        url = "https://maps.google.com/@38.4742,27.1125,15z"
        lat, lon = GeoUtils.extract_coords_from_map_url(url)
        self.assertEqual(lat, 38.4742)
        self.assertEqual(lon, 27.1125)
    
    def test_extract_coords_invalid_url(self):
        """Test coordinate extraction from invalid URL"""
        url = "https://example.com/no-coords"
        lat, lon = GeoUtils.extract_coords_from_map_url(url)
        self.assertIsNone(lat)
        self.assertIsNone(lon)
    
    @patch('requests.get')
    def test_get_driving_route_polyline_success(self, mock_get):
        """Test successful route polyline retrieval"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'status': 'OK',
            'routes': [{'overview_polyline': {'points': 'test_polyline'}}]
        }
        mock_get.return_value = mock_response
        
        polyline = GeoUtils.get_driving_route_polyline(38.0, 27.0, 38.5, 27.5, "test_key")
        self.assertEqual(polyline, 'test_polyline')
    
    @patch('requests.get')
    def test_get_driving_route_polyline_failure(self, mock_get):
        """Test failed route polyline retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'status': 'ZERO_RESULTS'}
        mock_get.return_value = mock_response
        
        polyline = GeoUtils.get_driving_route_polyline(38.0, 27.0, 38.5, 27.5, "test_key")
        self.assertIsNone(polyline)

class TestGeoCoder(unittest.TestCase):
    """Test geocoding functionality"""
    
    def setUp(self):
        self.geocoder = GeoCoder()
    
    def test_generate_address_attempts(self):
        """Test address attempt generation"""
        attempts = self.geocoder._generate_address_attempts(
            "Test Sokak 123", "KARŞIYAKA 4"
        )
        self.assertIsInstance(attempts, list)
        self.assertGreater(len(attempts), 1)
        self.assertIn("Test Sokak 123", attempts[0])
    
    @patch('geopy.geocoders.Nominatim.geocode')
    def test_get_coordinates_success(self, mock_geocode):
        """Test successful coordinate retrieval"""
        # Mock successful geocoding
        mock_location = Mock()
        mock_location.latitude = 38.123
        mock_location.longitude = 27.456
        mock_geocode.return_value = mock_location
        
        result = self.geocoder.get_coordinates_from_address("Test Address")
        self.assertEqual(result['lat'], 38.123)
        self.assertEqual(result['lon'], 27.456)
    
    @patch('geopy.geocoders.Nominatim.geocode')
    def test_get_coordinates_failure(self, mock_geocode):
        """Test failed coordinate retrieval"""
        mock_geocode.return_value = None
        
        result = self.geocoder.get_coordinates_from_address("Invalid Address")
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lon'])

class TestWeatherService(unittest.TestCase):
    """Test weather service functionality"""
    
    def setUp(self):
        self.weather_service = WeatherService()
    
    @patch('requests.get')
    def test_fetch_weather_data_success(self, mock_get):
        """Test successful weather data retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'cod': 200,
            'main': {'temp': 25.5},
            'weather': [{'description': 'açık'}]
        }
        mock_get.return_value = mock_response
        
        result = self.weather_service.fetch_weather_data()
        self.assertTrue(result['success'])
        self.assertEqual(result['temperature'], 25.5)
        self.assertEqual(result['description'], 'açık')
    
    @patch('requests.get')
    def test_fetch_weather_data_failure(self, mock_get):
        """Test failed weather data retrieval"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.weather_service.fetch_weather_data()
        self.assertIn('error', result)

class TestPharmacyScraper(unittest.TestCase):
    """Test pharmacy web scraper"""
    
    def setUp(self):
        self.geocoder = Mock()
        self.scraper = PharmacyScraper(self.geocoder)
    
    def test_extract_address(self):
        """Test address extraction from HTML"""
        # This would require creating mock HTML elements
        # For now, just test that the method exists
        self.assertTrue(hasattr(self.scraper, '_extract_address'))
    
    def test_extract_phone(self):
        """Test phone extraction from HTML"""
        self.assertTrue(hasattr(self.scraper, '_extract_phone'))
    
    def test_extract_map_url(self):
        """Test map URL extraction from HTML"""
        self.assertTrue(hasattr(self.scraper, '_extract_map_url'))

# GUI Tests (require QApplication)
class TestGUI(unittest.TestCase):
    """Test GUI components"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI tests"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def test_circular_label_creation(self):
        """Test circular label widget creation"""
        label = CircularQLabel()
        self.assertIsNotNone(label)
        self.assertEqual(label.sizeHint().width(), 120)
        self.assertEqual(label.sizeHint().height(), 120)
    
    def test_pharmacy_screen_creation(self):
        """Test pharmacy screen creation"""
        screen = PharmacyScreen()
        self.assertIsNotNone(screen)
        self.assertEqual(screen.target_region, Config.TARGET_REGION)
    
    def test_ad_screen_creation(self):
        """Test advertisement screen creation"""
        screen = AdScreen()
        self.assertIsNotNone(screen)
        self.assertEqual(screen.current_video_index, 0)
    
    def test_main_app_creation(self):
        """Test main application creation"""
        app = EczaneApp()
        self.assertIsNotNone(app)
        self.assertIsNotNone(app.pharmacy_screen)
        self.assertIsNotNone(app.ad_screen)

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_config_integration(self):
        """Test configuration integration with other components"""
        # Test that Config values are properly used
        self.assertIsInstance(Config.TARGET_REGION, str)
        self.assertIsInstance(Config.GOOGLE_MAPS_API_KEY, str)
        self.assertIsInstance(Config.OPENWEATHER_API_KEY, str)
    
    def test_pharmacy_data_flow(self):
        """Test complete pharmacy data flow"""
        # This would test the complete flow from web scraping to display
        # For now, just verify components can work together
        geocoder = GeoCoder()
        scraper = PharmacyScraper(geocoder)
        weather_service = WeatherService()
        
        # Test that components can be instantiated together
        self.assertIsNotNone(geocoder)
        self.assertIsNotNone(scraper)
        self.assertIsNotNone(weather_service)

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def test_missing_api_keys(self):
        """Test behavior with missing API keys"""
        # Test weather service with invalid key
        original_key = Config.OPENWEATHER_API_KEY
        Config.OPENWEATHER_API_KEY = ""
        
        weather_service = WeatherService()
        result = weather_service.fetch_weather_data()
        self.assertIn('error', result)
        
        # Restore original key
        Config.OPENWEATHER_API_KEY = original_key
    
    def test_network_errors(self):
        """Test network error handling"""
        with patch('requests.get', side_effect=Exception("Network error")):
            weather_service = WeatherService()
            result = weather_service.fetch_weather_data()
            self.assertIn('error', result)
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates"""
        lat, lon = GeoUtils.extract_coords_from_map_url("invalid_url")
        self.assertIsNone(lat)
        self.assertIsNone(lon)

class TestPerformance(unittest.TestCase):
    """Performance tests"""
    
    def test_address_generation_performance(self):
        """Test address generation performance"""
        import time
        
        geocoder = GeoCoder()
        start_time = time.time()
        
        # Generate address attempts multiple times
        for _ in range(100):
            attempts = geocoder._generate_address_attempts(
                "Test Sokak 123", "KARŞIYAKA 4"
            )
        
        elapsed_time = time.time() - start_time
        # Should complete within reasonable time (1 second for 100 iterations)
        self.assertLess(elapsed_time, 1.0)
    
    def test_config_validation_performance(self):
        """Test configuration validation performance"""
        import time
        
        start_time = time.time()
        for _ in range(50):
            Config.validate_config()
        elapsed_time = time.time() - start_time
        
        # Should be very fast
        self.assertLess(elapsed_time, 0.1)

if __name__ == '__main__':
    # Configure test environment
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestConfig, TestPharmacyData, TestGeoUtils, TestGeoCoder,
        TestWeatherService, TestPharmacyScraper, TestGUI,
        TestIntegration, TestErrorHandling, TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
