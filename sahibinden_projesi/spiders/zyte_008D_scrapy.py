import scrapy

class IlanDetaySpider(scrapy.Spider):
    name = "ilan_detay_spider"
    allowed_domains = ["sahibinden.com"]
    start_urls = [
        "https://www.sahibinden.com/ilan/vasita-otomobil-opel-ilk-ruhsat-sahibinden-alinma-degisensiz-kazasiz-1248665984/detay"
    ]

    def parse(self, response):
        self.log('Sayfa çekildi!')
        yield {
            "title": response.css('title::text').get(),
            "html": response.text,
        }
