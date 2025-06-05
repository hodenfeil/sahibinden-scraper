BOT_NAME = "sahibinden_projesi"

SPIDER_MODULES = ["sahibinden_projesi.spiders"]
NEWSPIDER_MODULE = "sahibinden_projesi.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Zyte API ayarları
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
}
ZYTE_API_ENABLED = True
REQUEST_FINGERPRINTER_CLASS = "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
HTTPERROR_ALLOWED_CODES = [403]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

# Encoding
FEED_EXPORT_ENCODING = "utf-8"

# Log seviyesi
LOG_LEVEL = "INFO"