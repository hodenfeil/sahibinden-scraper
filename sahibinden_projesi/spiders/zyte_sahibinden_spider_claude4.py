import scrapy


class ZyteSahibindenSpiderClaude4(scrapy.Spider):
    name = "zyte_sahibinden_spider_claude4"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        # Zyte API middleware'ini etkinleştir
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },
        # Zyte API ayarları
        "ZYTE_API_ENABLED": True,
        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # robots.txt'yi görmezden gel
        "ROBOTSTXT_OBEY": False,

        # 403 hatalarını parse metoduna gönder
        "HTTPERROR_ALLOWED_CODES": [403],

        # Gerçekçi User-Agent ekle
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        # Retry ayarları
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],
    }

    def start_requests(self):
        url = "https://www.sahibinden.com/ilan/vasita-otomobil-opel-ilk-ruhsat-sahibinden-alinma-degisensiz-kazasiz-1248665984/detay"

        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "zyte_api": {
                    "browserHtml": True,  # Tarayıcı modunda çalıştır
                    "geolocation": "TR",  # Türkiye IP'si kullan
                    "httpResponseBody": True,  # HTML içeriğini al
                    "screenshot": False,  # Ekran görüntüsü almaya gerek yok
                    "actions": [  # Sayfanın tam yüklenmesini bekle
                        {
                            "action": "waitForSelector",
                            "selector": "body",
                            "timeout": 10
                        }
                    ]
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

            # Sayfadan veri çekme örneği
            title = response.css('h1::text').get()
            price = response.css('.price::text').get()

            yield {
                "url": response.url,
                "status": response.status,
                "title": title,
                "price": price,
                "html_length": len(response.text),
                "html_preview": response.text[:1000]  # Tam HTML yerine önizleme
            }
        else:
            self.logger.warning(f"BEKLENMEDİK DURUM: {response.status}. Sayfa içeriği (ilk 500 karakter):")
            self.logger.warning(response.text[:500])
