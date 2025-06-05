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
        "DOWNLOAD_DELAY": 3,
        "RETRY_TIMES": 2,
        "RETRY_HTTP_CODES": [403, 500, 502, 503, 504, 408, 429],
        "DOWNLOAD_TIMEOUT": 120,
        "DNSCACHE_ENABLED": False,
    }

    def start_requests(self):
        # ZenRows API anahtarı
        zenrows_api_key = "67129c0a63f61c085f3d9bea1105129f0cdfa59e"

        # Hedef URL
        target_url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        # ZenRows API parametreleri (basit versiyon)
        params = {
            'url': target_url,
            'apikey': zenrows_api_key,
            'js_render': 'true',
            'premium_proxy': 'true',
            'proxy_country': 'tr',
            'wait': '3000',
        }

        # URL parametrelerini oluştur
        param_string = urllib.parse.urlencode(params)
        zenrows_url = f"https://api.zenrows.com/v1/?{param_string}"

        self.logger.info(f"ZenRows URL: {zenrows_url}")

        yield scrapy.Request(
            zenrows_url,
            callback=self.parse,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
            meta={"target_url": target_url}
        )

    def parse(self, response):
        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"Response length: {len(response.text)}")

        # Orijinal hedef URL'yi meta'dan al
        target_url = response.meta.get("target_url")

        if response.status == 200:
            self.logger.info("ZenRows API'den başarılı yanıt alındı")

            html_content = response.text

            # HTML'i dosyaya kaydet (debug için)
            try:
                with open('zenrows_response.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info("HTML dosyaya kaydedildi: zenrows_response.html")
            except Exception as e:
                self.logger.warning(f"HTML dosyaya kaydedilemedi: {e}")

            # Manuel CSS seçiciler
            title = (
                    response.css('h1[data-testid="classified-detail-title"]::text').get() or
                    response.css('h1.classifiedDetailTitle::text').get() or
                    response.css('h1::text').get() or
                    response.css('.classified-title::text').get()
            )

            price = (
                    response.css('[data-testid="classified-detail-price"]::text').get() or
                    response.css('.classifiedInfo .price::text').get() or
                    response.css('.price-text::text').get() or
                    response.css('span:contains("TL")::text').get()
            )

            location = (
                    response.css('[data-testid="classified-detail-location"]::text').get() or
                    response.css('.classifiedInfo .location::text').get() or
                    response.css('.location::text').get()
            )

            # Araç detayları - tablo yapısından çek
            year = response.css('td:contains("Yıl") + td::text').get()
            km = response.css('td:contains("KM") + td::text').get()
            fuel = response.css('td:contains("Yakıt") + td::text').get()
            brand = response.css('td:contains("Marka") + td::text').get()
            model = response.css('td:contains("Model") + td::text').get()
            gear = response.css('td:contains("Vites") + td::text').get()

            # Veri temizleme
            title = title.strip() if title else ''
            price = price.strip() if price else ''
            location = location.strip() if location else ''
            year = year.strip() if year else ''
            km = km.strip() if km else ''
            fuel = fuel.strip() if fuel else ''
            brand = brand.strip() if brand else ''
            model = model.strip() if model else ''
            gear = gear.strip() if gear else ''

            # HTML içeriğinde "sahibinden" kelimesi var mı kontrol et
            is_sahibinden_page = "sahibinden" in html_content.lower()

            # 403 hata sayfası mı kontrol et
            is_error_page = "error-page-container" in html_content

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
                "brand": brand,
                "model": model,
                "gear": gear,
                "html_length": len(html_content),
                "has_content": True,
                "is_sahibinden_page": is_sahibinden_page,
                "is_error_page": is_error_page,
                "html_preview": html_content[:500],
                "zenrows_success": True,
            }

        else:
            self.logger.warning(f"ZenRows API'den hata yanıtı: {response.status}")
            yield {
                "url": target_url,
                "zenrows_url": response.url,
                "status": response.status,
                "error": f"ZenRows API error: {response.status}",
                "html_length": len(response.text),
                "html_preview": response.text[:200],
                "zenrows_success": False
            }
