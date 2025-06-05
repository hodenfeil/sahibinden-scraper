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
        "DOWNLOAD_DELAY": 3,
        "RETRY_TIMES": 2,
        "RETRY_HTTP_CODES": [403, 500, 502, 503, 504, 408, 429],
        "DOWNLOAD_TIMEOUT": 120,  # 2 dakika timeout
        "DNSCACHE_ENABLED": False,
    }

    def start_requests(self):
        # ZenRows API anahtarı
        zenrows_api_key = "67129c0a63f61c085f3d9bea1105129f0cdfa59e"

        # Hedef URL
        target_url = "https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay"

        # CSS Extractor - ZenRows'un otomatik veri çıkarma özelliği
        css_extractor = json.dumps({
            "title": "h1, [data-testid='classified-detail-title']",
            "price": ".classifiedInfo .price, [data-testid='classified-detail-price'], .price-text",
            "location": ".classifiedInfo .location, [data-testid='classified-detail-location']",
            "year": "td:contains('Yıl') + td, .classified-property:contains('Yıl') .value",
            "km": "td:contains('KM') + td, .classified-property:contains('KM') .value",
            "fuel": "td:contains('Yakıt') + td, .classified-property:contains('Yakıt') .value",
            "brand": "td:contains('Marka') + td, .classified-property:contains('Marka') .value",
            "model": "td:contains('Model') + td, .classified-property:contains('Model') .value",
            "gear": "td:contains('Vites') + td, .classified-property:contains('Vites') .value"
        })

        # ZenRows API parametreleri
        params = {
            'url': target_url,
            'apikey': zenrows_api_key,
            'js_render': 'true',
            'premium_proxy': 'true',
            'proxy_country': 'tr',
            'css_extractor': css_extractor,
            'wait': '3000',  # 3 saniye bekle
        }

        # URL parametrelerini oluştur
        param_string = urllib.parse.urlencode(params)
        zenrows_url = f"https://api.zenrows.com/v1/?{param_string}"

        yield scrapy.Request(
            zenrows_url,
            callback=self.parse,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
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

                # CSS Extractor sonuçlarını al
                extracted_data = json_data.get('data', {})
                html_content = json_data.get('html', '')

                self.logger.info(f"HTML content length: {len(html_content)}")
                self.logger.info(f"Extracted data: {extracted_data}")

                # HTML'i dosyaya kaydet (debug için)
                try:
                    with open('zenrows_response.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.logger.info("HTML dosyaya kaydedildi: zenrows_response.html")
                except Exception as e:
                    self.logger.warning(f"HTML dosyaya kaydedilemedi: {e}")

                # CSS Extractor'dan gelen verileri kullan
                title = extracted_data.get('title', [''])[0] if extracted_data.get('title') else ''
                price = extracted_data.get('price', [''])[0] if extracted_data.get('price') else ''
                location = extracted_data.get('location', [''])[0] if extracted_data.get('location') else ''
                year = extracted_data.get('year', [''])[0] if extracted_data.get('year') else ''
                km = extracted_data.get('km', [''])[0] if extracted_data.get('km') else ''
                fuel = extracted_data.get('fuel', [''])[0] if extracted_data.get('fuel') else ''
                brand = extracted_data.get('brand', [''])[0] if extracted_data.get('brand') else ''
                model = extracted_data.get('model', [''])[0] if extracted_data.get('model') else ''
                gear = extracted_data.get('gear', [''])[0] if extracted_data.get('gear') else ''

                # Eğer CSS Extractor boş sonuç verdiyse, manuel CSS seçiciler kullan
                if not title and html_content:
                    from scrapy.http import HtmlResponse
                    html_response = HtmlResponse(
                        url=target_url,
                        body=html_content.encode('utf-8'),
                        encoding='utf-8'
                    )

                    title = (
                            html_response.css('h1[data-testid="classified-detail-title"]::text').get() or
                            html_response.css('h1.classifiedDetailTitle::text').get() or
                            html_response.css('h1::text').get() or
                            html_response.css('.classified-title::text').get()
                    )

                    price = (
                            html_response.css('[data-testid="classified-detail-price"]::text').get() or
                            html_response.css('.classifiedInfo .price::text').get() or
                            html_response.css('.price-text::text').get() or
                            html_response.css('span:contains("TL")::text').get()
                    )

                    location = (
                            html_response.css('[data-testid="classified-detail-location"]::text').get() or
                            html_response.css('.classifiedInfo .location::text').get() or
                            html_response.css('.location::text').get()
                    )

                # Veri temizleme
                title = title.strip() if title else ''
                price = price.strip() if price else ''
                location = location.strip() if location else ''
                year = year.strip() if year else ''
                km = km.strip() if km else ''
                fuel = fuel.strip() if fuel else ''

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
                    "extracted_data": extracted_data,  # Ham çıkarılan veri
                }

            except json.JSONDecodeError:
                # JSON değilse, düz HTML olarak işle
                self.logger.info("JSON parse edilemedi, düz HTML olarak işleniyor")
                html_content = response.text

                # Manuel CSS seçiciler
                from scrapy.http import HtmlResponse
                html_response = HtmlResponse(
                    url=target_url,
                    body=html_content.encode('utf-8'),
                    encoding='utf-8'
                )

                title = (
                        html_response.css('h1[data-testid="classified-detail-title"]::text').get() or
                        html_response.css('h1.classifiedDetailTitle::text').get() or
                        html_response.css('h1::text').get()
                )

                price = (
                        html_response.css('[data-testid="classified-detail-price"]::text').get() or
                        html_response.css('.classifiedInfo .price::text').get() or
                        html_response.css('.price-text::text').get()
                )

                location = (
                        html_response.css('[data-testid="classified-detail-location"]::text').get() or
                        html_response.css('.classifiedInfo .location::text').get() or
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
                    "zenrows_success": True,
                    "method": "manual_css"
                }

        else:
            self.logger.warning("ZenRows API'den hata yanıtı")
            yield {
                "url": target_url,
                "zenrows_url": response.url,
                "status": response.status,
                "error": f"ZenRows API error: {response.status}",
                "html_length": len(response.text),
                "html_preview": response.text[:200],
                "zenrows_success": False
            }
