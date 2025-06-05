import scrapy
import urllib.parse


class ZenRowsSahibindenSpider(scrapy.Spider):
    name = "zenrows_sahibinden_spider"
    allowed_domains = ["api.zenrows.com", "sahibinden.com"]

    custom_settings = {
        # ZenRows kullandığımız için Zyte middleware'lerini kaldır
        "DOWNLOADER_MIDDLEWARES": {},

        # Diğer ayarlar
        "ROBOTSTXT_OBEY": False,
        "HTTPERROR_ALLOWED_CODES": [403, 503],
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 5,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [403, 500, 502, 503, 504, 408, 429],
    }

    def start_requests(self):
        # ZenRows API anahtarı
        zenrows_api_key = "67129c0a63f61c085f3d9bea1105129f0cdfa59e"

        # Hedef URL
        target_url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        # URL'yi encode et
        encoded_url = urllib.parse.quote(target_url, safe='')

        # ZenRows API URL'sini oluştur
        zenrows_url = f"https://api.zenrows.com/v1/?apikey={zenrows_api_key}&url={encoded_url}&js_render=true&premium_proxy=true"

        yield scrapy.Request(
            zenrows_url,
            callback=self.parse,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
            },
            meta={"target_url": target_url}
        )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"HTML length: {len(response.text)}")
        self.logger.info(f"ZenRows API URL: {response.url}")

        # Orijinal hedef URL'yi meta'dan al
        target_url = response.meta.get("target_url")

        if response.status == 200 and len(response.text) > 1000:
            self.logger.info("HTML içeriği mevcut, işleniyor...")

            # HTML'i dosyaya kaydet (debug için)
            try:
                with open('zenrows_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.logger.info("HTML dosyaya kaydedildi: zenrows_response.html")
            except Exception as e:
                self.logger.warning(f"HTML dosyaya kaydedilemedi: {e}")

            # Sahibinden.com için CSS seçiciler
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

            # 403 hata sayfası mı kontrol et
            is_error_page = "error-page-container" in response.text

            yield {
                "url": target_url,
                "zenrows_url": response.url,
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
                "is_error_page": is_error_page,
                "html_preview": response.text[:500]
            }
        else:
            self.logger.warning("Yetersiz HTML içeriği veya hata durumu")
            yield {
                "url": target_url,
                "zenrows_url": response.url,
                "status": response.status,
                "error": "Insufficient HTML content or HTTP error",
                "html_length": len(response.text),
                "html_preview": response.text[:200]
            }
