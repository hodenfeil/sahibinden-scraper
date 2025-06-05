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
        "HTTPERROR_ALLOWED_CODES": [403],
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 1,
    }

    def start_requests(self):
        # Playground'da çalışan URL'yi kullan
        url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "zyte_api": {
                    # Playground'da çalışan parametreleri birebir kullan
                    "browserHtml": True,
                    "geolocation": "TR",
                    "javascript": True,
                    # Ek parametreler eklemiyoruz, playground'daki gibi minimal tutuyoruz
                }
            }
        )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"HTML length: {len(response.text)}")

        # 403 olsa bile HTML'i kontrol et
        if len(response.text) > 1000:  # Yeterli HTML varsa işle
            self.logger.info("HTML içeriği mevcut, işleniyor...")

            # HTML'i dosyaya kaydet
            with open('response_403.html', 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Veri çıkarmayı dene
            title = response.css('h1::text').get()
            price = response.css('.classifiedInfo h3::text').get()

            yield {
                "url": response.url,
                "status": response.status,
                "title": title,
                "price": price,
                "html_length": len(response.text),
                "has_content": True
            }
        else:
            self.logger.warning("Yetersiz HTML içeriği")
