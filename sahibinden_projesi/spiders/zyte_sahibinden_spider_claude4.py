import scrapy
import urllib.parse
import json


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

        # ZenRows API parametreleri (playground'daki gibi)
        params = {
            'url': target_url,
            'apikey': zenrows_api_key,
            'js_render': 'true',
            'json_response': 'true',
            'js_instructions': '[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]',
            'premium_proxy': 'true',
            'proxy_country': 'tr',
        }

        # URL parametrelerini oluştur
        param_string = urllib.parse.urlencode(params)
        zenrows_url = f"https://api.zenrows.com/v1/?{param_string}"

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
        self.logger.info(f"Response length: {len(response.text)}")
        self.logger.info(f"ZenRows API URL: {response.url}")

        # Orijinal hedef URL'yi meta'dan al
        target_url = response.meta.get("target_url")

        if response.status == 200:
            self.logger.info("ZenRows API'den başarılı yanıt alındı")

            try:
                # JSON response'u parse et
                json_data = json.loads(response.text)
                html_content = json_data.get('html', '')

                self.logger.info(f"HTML content length: {len(html_content)}")

                # HTML'i dosyaya kaydet (debug için)
                try:
                    with open('zenrows_response.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.logger.info("HTML dosyaya kaydedildi: zenrows_response.html")
                except Exception as e:
                    self.logger.warning(f"HTML dosyaya kaydedilemedi: {e}")

                # HTML'i Scrapy response'una dönüştür
                from scrapy.http import HtmlResponse
                html_response = HtmlResponse(
                    url=target_url,
                    body=html_content.encode('utf-8'),
                    encoding='utf-8'
                )

                # Sahibinden.com için CSS seçiciler
                title = (
                        html_response.css('h1.classifiedDetailTitle::text').get() or
                        html_response.css('h1::text').get() or
                        html_response.css('.classifiedDetailTitle::text').get()
                )

                price = (
                        html_response.css('.classifiedInfo h3::text').get() or
                        html_response.css('.price::text').get() or
                        html_response.css('h3:contains("TL")::text').get()
                )

                location = (
                        html_response.css('.classifiedInfo ul li:contains("İl") span::text').get() or
                        html_response.css('.location::text').get()
                )

                # Araç detayları
                year = html_response.css('.classifiedInfo ul li:contains("Yıl") span::text').get()
                km = html_response.css('.classifiedInfo ul li:contains("KM") span::text').get()
                fuel = html_response.css('.classifiedInfo ul li:contains("Yakıt") span::text').get()

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
                    "html_length": len(html_content),
                    "has_content": True,
                    "is_sahibinden_page": is_sahibinden_page,
                    "is_error_page": is_error_page,
                    "html_preview": html_content[:500],
                    "zenrows_success": True
                }

            except json.JSONDecodeError:
                # JSON değilse, düz HTML olarak işle
                self.logger.info("JSON parse edilemedi, düz HTML olarak işleniyor")
                html_content = response.text

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
                    "html_length": len(html_content),
                    "has_content": True,
                    "is_sahibinden_page": is_sahibinden_page,
                    "is_error_page": is_error_page,
                    "html_preview": html_content[:500],
                    "zenrows_success": True
                }

        else:
            self.logger.warning("ZenRows API'den hata yanıtı")
            yield {
                "url": target_url,
                "zenrows_url": response.url,
                "status": response.status,
                "error": "ZenRows API error",
                "html_length": len(response.text),
                "html_preview": response.text[:200],
                "zenrows_success": False
            }
