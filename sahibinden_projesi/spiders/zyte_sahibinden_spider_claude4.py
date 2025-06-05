import scrapy
import requests


class ZenRowsRequestsSpider(scrapy.Spider):
    name = "zenrows_requests_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {},
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 2,
        "AUTOTHROTTLE_ENABLED": False,
    }

    def start_requests(self):
        yield scrapy.Request("http://httpbin.org/get", callback=self.parse_with_zenrows)

    def parse_with_zenrows(self, response):
        # ZenRows API'yi requests ile çağır
        zenrows_url = "https://api.zenrows.com/v1/"
        params = {
            'url': 'https://www.sahibinden.com/ilan/vasita-otomobil-renault-2022-megane-4-joy-1.3tce-140hpedc-degisensz-tramersz-tesla-ekran-1242514779/detay',
            'apikey': '67129c0a63f61c085f3d9bea1105129f0cdfa59e',
            'js_render': 'true',
            'premium_proxy': 'true',
            'proxy_country': 'tr',
            'wait': '10000'
        }

        try:
            self.logger.info("ZenRows API çağrısı başlatılıyor...")
            api_response = requests.get(zenrows_url, params=params, timeout=120)

            if api_response.status_code == 200:
                self.logger.info(f"Başarılı! HTML uzunluğu: {len(api_response.text)}")

                # Veri çıkarma
                from scrapy.http import HtmlResponse
                html_response = HtmlResponse(
                    url=params['url'],
                    body=api_response.text.encode('utf-8'),
                    encoding='utf-8'
                )

                title = html_response.css('h1::text').get()
                price = html_response.css('span:contains("TL")::text').get()

                yield {
                    "url": params['url'],
                    "title": title.strip() if title else '',
                    "price": price.strip() if price else '',
                    "html_length": len(api_response.text),
                    "status": "success"
                }
            else:
                self.logger.error(f"API hatası: {api_response.status_code}")
                yield {"error": f"API error: {api_response.status_code}"}

        except Exception as e:
            self.logger.error(f"Request hatası: {e}")
            yield {"error": str(e)}
