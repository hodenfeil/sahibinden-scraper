import scrapy


class ZyteSahibindenSpiderWorking(scrapy.Spider):
    name = "zyte_sahibinden_spider_working"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },
        "ZYTE_API_KEY": "d57e4ad5f6954893b785101356b9ec20",
        "ZYTE_API_ENABLED": True,
        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "ROBOTSTXT_OBEY": False,
        "HTTPERROR_ALLOWED_CODES": [403],
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 3,
        "RETRY_TIMES": 1,  # Retry'ı azalt
    }

    def start_requests(self):
        # Daha basit URL'lerle test et
        test_urls = [
            "https://www.sahibinden.com",
            "https://www.sahibinden.com/vasita/otomobil",
            "https://www.sahibinden.com/vasita/otomobil/renault",
        ]

        for url in test_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "zyte_api": {
                        "browserHtml": True,
                        "geolocation": "US",  # TR yerine US dene
                        "javascript": True,
                    }
                }
            )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status} for {response.url}")
        self.logger.info(f"HTML length: {len(response.text)}")

        if response.status == 200:
            self.logger.info("BAŞARILI! 200 OK alındı")

            # Ana sayfa veya kategori sayfasından ilan linklerini çek
            ilan_links = response.css('a[href*="/ilan/"]::attr(href)').getall()
            self.logger.info(f"Bulunan ilan sayısı: {len(ilan_links)}")

            # İlk 3 ilan linkini test et
            for link in ilan_links[:3]:
                if link.startswith('/'):
                    full_url = f"https://www.sahibinden.com{link}"
                else:
                    full_url = link

                yield scrapy.Request(
                    full_url,
                    callback=self.parse_detail,
                    meta={
                        "zyte_api": {
                            "browserHtml": True,
                            "geolocation": "US",
                            "javascript": True,
                        }
                    }
                )

            yield {
                "url": response.url,
                "status": response.status,
                "page_type": "listing",
                "ilan_count": len(ilan_links),
                "success": True
            }

        elif len(response.text) > 1000:
            # 403 olsa bile içerik varsa kaydet
            yield {
                "url": response.url,
                "status": response.status,
                "html_length": len(response.text),
                "page_type": "error_page"
            }

    def parse_detail(self, response):
        """İlan detay sayfalarını işle"""
        self.logger.info(f"Detail page status: {response.status}")

        if response.status == 200:
            title = response.css('h1::text').get()
            price = response.css('.classifiedInfo h3::text').get()

            yield {
                "url": response.url,
                "status": response.status,
                "title": title,
                "price": price,
                "page_type": "detail",
                "success": True
            }
