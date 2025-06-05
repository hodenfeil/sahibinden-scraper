import scrapy


class ZyteSahibindenSpiderClaude4(scrapy.Spider):
    name = "zyte_sahibinden_spider_claude4"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        # Zyte API middleware'ini etkinleştir - EN ÖNEMLİ AYAR!
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },

        # Zyte API anahtarını buraya ekleyin (güvenlik için Scrapy Cloud Settings'den de ekleyebilirsiniz)
        "ZYTE_API_KEY": "d57e4ad5f6954893b785101356b9ec20",

        # Zyte API'yi etkinleştir
        "ZYTE_API_ENABLED": True,

        # Request fingerprinter'ı Zyte API uyumlu yap
        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",

        # Async reactor kullan
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # robots.txt'yi görmezden gel
        "ROBOTSTXT_OBEY": False,

        # 403 hatalarını parse metoduna gönder
        "HTTPERROR_ALLOWED_CODES": [403],

        # Gerçekçi User-Agent
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        # Retry ayarları
        "RETRY_TIMES": 2,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],

        # Concurrent requests'i azalt
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
    }

    def start_requests(self):
        # Test için daha basit bir URL deneyelim
        urls = [
            "https://www.sahibinden.com/ilan/vasita-otomobil-opel-ilk-ruhsat-sahibinden-alinma-degisensiz-kazasiz-1248665984/detay",
            "https://www.sahibinden.com/vasita-otomobil",  # Fallback URL
        ]

        for url in urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "zyte_api": {
                        "browserHtml": True,
                        "geolocation": "TR",
                        "httpResponseBody": True,
                        "screenshot": False,
                        "actions": [
                            {
                                "action": "waitForTimeout",
                                "timeout": 3000  # 3 saniye bekle
                            }
                        ]
                    }
                },
                dont_filter=True
            )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status} for URL: {response.url}")
        self.logger.info(f"Response headers: {dict(response.headers)}")

        if response.status == 403:
            self.logger.warning("403 HATASI ALINDI! Sayfa içeriği (ilk 1000 karakter):")
            self.logger.warning(response.text[:1000])

            # 403 durumunda bile bazı bilgileri kaydet
            yield {
                "url": response.url,
                "status": response.status,
                "error": "403 Forbidden",
                "html_preview": response.text[:500]
            }
            return

        if response.status == 200:
            self.logger.info("BAŞARILI (200)! Sayfa yüklendi.")
            self.logger.info(f"Sayfa boyutu: {len(response.text)} karakter")

            # Sayfadan temel bilgileri çek
            title = response.css('h1::text').get() or response.css('title::text').get()

            yield {
                "url": response.url,
                "status": response.status,
                "title": title,
                "html_length": len(response.text),
                "success": True,
                "html_preview": response.text[:1000]
            }
        else:
            self.logger.warning(f"BEKLENMEDİK DURUM: {response.status}")
            yield {
                "url": response.url,
                "status": response.status,
                "error": f"Unexpected status: {response.status}"
            }
