#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude - Setup Script
Installation and packaging configuration for the pharmacy display system
"""

from setuptools import setup, find_packages
import os
import sys

# Read README for long description
def read_readme():
    """Read README.md for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Modern nöbetçi eczane gösterge sistemi"

# Read requirements
def read_requirements():
    """Read requirements.txt"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    
    return requirements

# Version information
VERSION = '2.0.0'
AUTHOR = 'Claude Project Team'
AUTHOR_EMAIL = 'info@claude.com'
DESCRIPTION = 'Modern nöbetçi eczane gösterge sistemi - PyQt5 tabanlı şık arayüz'
URL = 'https://github.com/yourusername/claude'

# Platform-specific requirements
def get_platform_requirements():
    """Get platform-specific requirements"""
    requirements = read_requirements()
    
    # Add platform-specific packages
    if sys.platform.startswith('linux'):
        # Linux-specific packages
        pass
    elif sys.platform.startswith('win'):
        # Windows-specific packages
        pass
    elif sys.platform.startswith('darwin'):
        # macOS-specific packages
        pass
    
    return requirements

# Console scripts
CONSOLE_SCRIPTS = [
    'claude=main:main',
    'eczane-display=main:main',
]

# GUI scripts (for Windows)
GUI_SCRIPTS = []
if sys.platform.startswith('win'):
    GUI_SCRIPTS = [
        'claude-gui=main:main',
    ]

# Package data
PACKAGE_DATA = {
    '': [
        '*.png',
        '*.jpg',
        '*.ico',
        '*.md',
        '*.txt',
        '*.yaml',
        '*.yml',
        '*.json',
    ]
}

# Data files
DATA_FILES = [
    ('', ['README.md', 'requirements.txt', '.gitignore']),
]

# Classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Healthcare Industry',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Office/Business :: Financial',
    'Topic :: Multimedia :: Graphics :: Viewers',
    'Environment :: X11 Applications :: Qt',
    'Natural Language :: Turkish',
]

# Keywords
KEYWORDS = [
    'eczane', 'nöbetçi', 'pharmacy', 'healthcare', 'medical',
    'pyqt5', 'gui', 'display', 'digital-signage', 'turkey',
    'izmir', 'maps', 'weather', 'qr-codes'
]

# Extra requirements for different use cases
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=7.4.3',
        'pytest-qt>=4.2.0',
        'black>=23.9.1',
        'flake8>=6.1.0',
        'mypy>=1.6.0',
        'pre-commit>=3.5.0',
    ],
    'test': [
        'pytest>=7.4.3',
        'pytest-qt>=4.2.0',
        'pytest-cov>=4.1.0',
        'pytest-mock>=3.12.0',
    ],
    'build': [
        'pyinstaller>=6.0.0',
        'setuptools>=68.0.0',
        'wheel>=0.41.0',
        'twine>=4.0.0',
    ],
    'docs': [
        'sphinx>=7.2.0',
        'sphinx-rtd-theme>=1.3.0',
        'myst-parser>=2.0.0',
    ]
}

# All optional dependencies
EXTRAS_REQUIRE['all'] = list(set(
    dep for deps in EXTRAS_REQUIRE.values() for dep in deps
))

setup(
    name='claude',
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url=URL,
    
    # Package information
    packages=find_packages(),
    py_modules=['main', 'config'],
    include_package_data=True,
    package_data=PACKAGE_DATA,
    data_files=DATA_FILES,
    
    # Requirements
    python_requires='>=3.8',
    install_requires=get_platform_requirements(),
    extras_require=EXTRAS_REQUIRE,
    
    # Scripts
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
        'gui_scripts': GUI_SCRIPTS,
    },
    
    # Metadata
    classifiers=CLASSIFIERS,
    keywords=' '.join(KEYWORDS),
    license='MIT',
    
    # Additional metadata
    project_urls={
        'Bug Reports': f'{URL}/issues',
        'Source': URL,
        'Documentation': f'{URL}#readme',
        'Funding': f'{URL}/sponsors',
    },
    
    # Packaging options
    zip_safe=False,
    
    # Options for different platforms
    options={
        'build_exe': {
            'packages': [
                'PyQt5', 'requests', 'beautifulsoup4', 'geopy', 
                'PIL', 'qrcode', 'lxml'
            ],
            'include_files': [
                'logo.png', 'README.md', 'config.py'
            ],
            'excludes': [
                'tkinter', 'unittest', 'pydoc', 'doctest'
            ]
        },
        'bdist_mac': {
            'bundle_name': 'Claude Eczane Display',
            'iconfile': 'logo.icns',
        },
        'bdist_dmg': {
            'applications_shortcut': True,
            'volume_label': 'Claude Installer',
        }
    }
)

# Post-installation setup
def post_install():
    """Post-installation setup tasks"""
    import os
    
    # Create necessary directories
    dirs_to_create = ['ads', 'logs', 'cache']
    
    for directory in dirs_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
    
    # Create sample configuration if it doesn't exist
    config_example = """# Claude Configuration Example
# Copy this to config_local.py and customize

# API Keys (get from respective services)
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"
OPENWEATHER_API_KEY = "your_openweather_api_key_here"

# Target region for pharmacy filtering
TARGET_REGION = "KARŞIYAKA 4"

# Enable/disable features
ENABLE_WEATHER = True
ENABLE_MAPS = True
ENABLE_QR_CODES = True
ENABLE_ADVERTISEMENTS = True
"""
    
    config_example_path = 'config_example.py'
    if not os.path.exists(config_example_path):
        with open(config_example_path, 'w', encoding='utf-8') as f:
            f.write(config_example)
        print(f"Created example configuration: {config_example_path}")
    
    print("\n" + "="*50)
    print("Claude Installation Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Configure your API keys in config.py or environment variables")
    print("2. Add your logo.png file to the main directory")
    print("3. Add advertisement videos to the ads/ folder")
    print("4. Run: python main.py")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    # Run post-installation tasks
    if 'install' in sys.argv:
        import atexit
        atexit.register(post_install) 
