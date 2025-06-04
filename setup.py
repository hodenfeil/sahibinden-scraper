# setup.py
from setuptools import setup, find_packages

setup(
    name         = 'sahibinden_projesi',
    version      = '1.5',  # <-- YENİ SÜRÜM!
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = sahibinden_projesi.settings']},
)