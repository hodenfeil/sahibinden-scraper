import scrapy


class ZyteSahibindenSpiderWorking(scrapy.Spider):
    name = "zyte_sahibinden_spider_working"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        # Zyte API middleware'ini etkinleştir
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },

        # API anahtarı
        "ZYTE_API_KEY": "d57e4ad5f6954893b785101356b9ec20",
        "ZYTE_API_ENABLED": True,

        # Request fingerprinter
        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",

        # Reactor
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # Diğer ayarlar
        "ROBOTSTXT_OBEY": False,
        "HTTPERROR_ALLOWED_CODES": [403, 503],
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [403, 500, 502, 503, 504, 408, 429],
    }

    def start_requests(self):
        # Playground'da çalışan URL'yi kullan
        url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "zyte_api": {
                    "browserHtml": True,
                    "geolocation": "TR",
                    "javascript": True,
                    "actions": [
                        {
                            "action": "waitForTimeout",
                            "timeout": 5000
                        },
                        {
                            "action": "waitForSelector",
                            "selector": "body",
                            "timeout": 10000
                        }
                    ],
                    "requestHeaders": {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                }
            }
        )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"HTML length: {len(response.text)}")
        self.logger.info(f"Response URL: {response.url}")

        # 403 olsa bile HTML'i kontrol et
        if len(response.text) > 1000:  # Yeterli HTML varsa işle
            self.logger.info("HTML içeriği mevcut, işleniyor...")

            # HTML'i dosyaya kaydet (debug için)
            try:
                with open('response_debug.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.logger.info("HTML dosyaya kaydedildi: response_debug.html")
            except Exception as e:
                self.logger.warning(f"HTML dosyaya kaydedilemedi: {e}")

            # Sahibinden.com için daha spesifik CSS seçiciler
            title = (
                    response.css('h1.classifiedDetailTitle::text').get() or
                    response.css('h1::text').get() or
                    response.css('.classifiedDetailTitle::text').get()
            )

            price = (
                    response.css('.classifiedInfo h3::text').get() or
                    response.css('.price::text').get() or
                    response.css('h3:contains("TL")::text').get()
            )

            location = (
                    response.css('.classifiedInfo ul li:contains("İl") span::text').get() or
                    response.css('.location::text').get()
            )

            # Araç detayları
            year = response.css('.classifiedInfo ul li:contains("Yıl") span::text').get()
            km = response.css('.classifiedInfo ul li:contains("KM") span::text').get()
            fuel = response.css('.classifiedInfo ul li:contains("Yakıt") span::text').get()

            # HTML içeriğinde "sahibinden" kelimesi var mı kontrol et
            is_sahibinden_page = "sahibinden" in response.text.lower()

            yield {
                "url": response.url,
                "status": response.status,
                "title": title,
                "price": price,
                "location": location,
                "year": year,
                "km": km,
                "fuel": fuel,
                "html_length": len(response.text),
                "has_content": True,
                "is_sahibinden_page": is_sahibinden_page,
                "html_preview": response.text[:500]  # İlk 500 karakter
            }
        else:
            self.logger.warning("Yetersiz HTML içeriği")
            yield {
                "url": response.url,
                "status": response.status,
                "error": "Insufficient HTML content",
                "html_length": len(response.text),
                "html_preview": response.text[:200]
            }
