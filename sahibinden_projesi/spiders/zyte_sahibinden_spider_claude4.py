import scrapy

class ZyteSahibindenSpider(scrapy.Spider):
    name = "zyte_sahibinden_spider"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },
        # Zyte API anahtarını Scrapy Cloud'da "ZYTE_API_KEY" olarak ayarlayın!
        "ZYTE_API_ENABLED": True,
        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "ROBOTSTXT_OBEY": False,
        "HTTPERROR_ALLOWED_CODES": [403],
        # User-Agent eklemek çoğu zaman 403'ü önler:
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        url = "https://www.sahibinden.com/ilan/vasita-otomobil-opel-ilk-ruhsat-sahibinden-alinma-degisensiz-kazasiz-1248665984/detay"
        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "zyte_api": {
                    "browserHtml": True,
                    "geolocation": "TR",
                    "httpResponseBody": True,
                }
            }
        )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status} for URL: {response.url}")

        if response.status == 403:
            self.logger.warning("403 HATASI ALINDI! Sayfa içeriği (ilk 1000 karakter):")
            self.logger.warning(response.text[:1000])
            return

        if response.status == 200:
            self.logger.info("BAŞARILI (200)! Sayfa içeriği (ilk 500 karakter):")
            self.logger.info(response.text[:500])
            yield {
                "url": response.url,
                "status": response.status,
                "html": response.text,
            }
        else:
            self.logger.warning(f"BEKLENMEDİK DURUM: {response.status}. Sayfa içeriği (ilk 500 karakter):")
            self.logger.warning(response.text[:500])
