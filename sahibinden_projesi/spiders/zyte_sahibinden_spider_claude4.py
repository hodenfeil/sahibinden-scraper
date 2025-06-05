import scrapy

class ZyteSahibindenSpiderClaude4(scrapy.Spider):
    name = "zyte_sahibinden_spider_claude4"  # Benzersiz bir isim
    allowed_domains = ["sahibinden.com"]

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