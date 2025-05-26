# setup.py
from setuptools import setup, find_packages

setup(
    name         = 'sahibinden_projesi',
    version      = '1.4',  # <-- Sürümü güncelledik! Bir sonraki deploy'da 1.4 yapın.
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = sahibinden_projesi.settings']},
)