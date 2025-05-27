# sahibinden_projesi/spiders/quotes_spider.py
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]

    custom_settings = {
        # Bu test için Zyte API'yi tamamen devre dışı bırakıyoruz
        "ZYTE_API_ENABLED": False,
        # Diğer özel ayarları da devre dışı bırakalım (gerekirse)
        "DOWNLOADER_MIDDLEWARES": {},  # Varsayılan Scrapy middleware'leri kullanılır
        "ROBOTSTXT_OBEY": True,  # Test sitesi için sorun olmaz
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",  # Bu kalabilir
    }

    def start_requests(self):
        # Bu örümcek için özel bir log mesajı ekleyelim
        self.log("<<<<< QUOTES SPIDER (TEST) BAŞLIYOR! >>>>>")
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.log(f"BAŞARILI! {response.url} adresi çekildi, durum {response.status}")

        quotes = response.css('div.quote')
        self.log(f"{len(quotes)} adet alıntı bulundu.")

        for quote in quotes:
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
            }

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)