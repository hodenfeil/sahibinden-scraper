import scrapy
from zenrows import ZenRowsClient


class ZenRowsDirectSpider(scrapy.Spider):
    name = "zenrows_direct_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {},
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "DOWNLOAD_TIMEOUT": 180,
        "AUTOTHROTTLE_ENABLED": False,
    }

    def start_requests(self):
        # Boş bir request ile başla
        yield scrapy.Request("http://httpbin.org/get", callback=self.parse_with_zenrows)

    def parse_with_zenrows(self, response):
        # ZenRows client'ı kullan
        client = ZenRowsClient("67129c0a63f61c085f3d9bea1105129f0cdfa59e")
        url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        params = {
            "js_render": "true",
            "premium_proxy": "true",
            "proxy_country": "tr",
            "wait": "10000"
        }

        try:
            self.logger.info("ZenRows API çağrısı başlatılıyor...")
            zenrows_response = client.get(url, params=params)
            self.logger.info(f"ZenRows yanıt alındı. Uzunluk: {len(zenrows_response.text)}")

            # HTML'i dosyaya kaydet (Scrapy Cloud'da da çalışır)
            try:
                with open("sahibinden_zenrows_cloud.html", "w", encoding="utf-8") as f:
                    f.write(zenrows_response.text)
                self.logger.info("HTML dosyaya kaydedildi")
            except Exception as e:
                self.logger.warning(f"Dosya kaydetme hatası: {e}")

            # Veri çıkarma
            from scrapy.http import HtmlResponse
            html_response = HtmlResponse(
                url=url,
                body=zenrows_response.text.encode('utf-8'),
                encoding='utf-8'
            )

            # CSS seçiciler ile veri çek
            title = (
                    html_response.css('h1::text').get() or
                    html_response.css('.classifiedDetailTitle::text').get()
            )

            price = (
                    html_response.css('.classifiedInfo .price::text').get() or
                    html_response.css('span:contains("TL")::text').get()
            )

            # Araç detayları
            year = html_response.css('td:contains("Yıl") + td::text').get()
            km = html_response.css('td:contains("KM") + td::text').get()
            fuel = html_response.css('td:contains("Yakıt") + td::text').get()

            yield {
                "url": url,
                "title": title.strip() if title else '',
                "price": price.strip() if price else '',
                "year": year.strip() if year else '',
                "km": km.strip() if km else '',
                "fuel": fuel.strip() if fuel else '',
                "html_length": len(zenrows_response.text),
                "status": "success",
                "method": "zenrows_direct"
            }

        except Exception as e:
            self.logger.error(f"ZenRows API hatası: {e}")
            yield {
                "url": url,
                "error": str(e),
                "status": "failed",
                "method": "zenrows_direct"
            }
