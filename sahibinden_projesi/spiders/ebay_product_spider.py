# sahibinden_projesi/spiders/ebay_product_spider.py
import scrapy


class EbayProductSpider(scrapy.Spider):
    name = "ebay_product_spider"
    allowed_domains = ["ebay.com"]  # Sadece ebay.com'dan veri çek

    # Buraya kazımak istediğiniz 100 eBay ürün linkini ekleyin
    # Örnek olarak birkaç link ekledim, kendi linklerinizle değiştirin
    start_urls = [
        "https://www.ebay.com/itm/167192345444?_skw=children+toys&itmmeta=01JW8NQ2V67RGAWJH131Y7N779&hash=item26ed70bb64:g:tb0AAOSwd45nZXj-&itmprp=enc%3AAQAKAAAAwFkggFvd1GGDu0w3yXCmi1e26bAcH8nMMbDvHIjcfsqKLTFZP5q1%2Bcj5Nwk2dnbPxpne4wvoqwgAb01RNnBqQXQ2DPFaUWMCIJdxdKnb8K5um%2BQt2w%2FmRCnxb5TaJJcYtiXO55cWF3E02mdYeLQF9aD7wfTCh4Ce34zeDRCgJRsO%2BJWq5Q9Wrg7EwCqOxiqR1L%2FgLs3ZfbWrUAPVM36xOWUhZoP8hlAi3dRI0qUgVuGJJPe7jSoJyT6Hq8K%2FghweJA%3D%3D%7Ctkp%3ABlBMUPit3JXiZQ",  # Kendi linkinizle değiştirin
        "https://www.ebay.com/itm/146383545414?_skw=children+toys&itmmeta=01JW8NQ2V6X78FFAKXV1XSFV5T&hash=item221523a446:g:d7AAAOSwq3xnq509&itmprp=enc%3AAQAKAAAA8FkggFvd1GGDu0w3yXCmi1fhTuJbtfqcwUFDzS4stH8f%2FuHNaKR0JZ5FhLkOHh7M9hB0W3I%2ByRPNFXn3gZQET%2BuHSeAhKiTjZNba52y6ULC%2BhiVPQ8mawQx6s8UTAHLL14Ozh7bQJNWShWgjKI73%2BZgYLdNCkHAFRvNybevvq2Ow9NZRugpe7QfbNO%2FaVb8bARYk31s%2F9z5gY880pwGBLB4cGr0cWUbP4wFgPAtVVJ%2FZC8GZO3j2OXqKjABpzAeeoqy%2BIIKl8YzW4e%2BHFRMIbVpP%2BKL8tGkOnEF03isaKnjh6j49pZy3UD%2B6K7hIJspZDg%3D%3D%7Ctkp%3ABk9SR_it3JXiZQ",  # Kendi linkinizle değiştirin
        "https://www.ebay.com/itm/405338259036?_skw=children+toys&itmmeta=01JW8NQ2V66B2ARPVY86WVPZ2Y&hash=item5e600afe5c:g:1bwAAOSwVD5nLo6V&itmprp=enc%3AAQAKAAAA0FkggFvd1GGDu0w3yXCmi1dwbVFKamIFA1D8aakb11ccABQewbhy%2BySHK1ONpPwQuctu86d17Q0IapeVNFVjthEBk7H%2F1C6v8B5IG5FAEOoDLUx0FAkfoLw4MOLEnQFRk4IT60SWCo%2Fo3%2FZ7vy7KwFy1KilQ1%2BYdBg7lGVIK12rjrJd1J5TrXXo4SrlGtUFU%2F3tfDqgoS3zqF7ekhfhXaKumhqehZcGDYxA39%2B9n8ku45GoYMAQfYE8LI7v2vq1lLS5Wi7uSat90XikD0IsPN%2B0%3D%7Ctkp%3ABk9SR_it3JXiZQ",
        "https://www.ebay.com/itm/195590318064?_skw=children+toys&itmmeta=01JW8NQ2V6CS4C1J74RXE3EA72&hash=item2d8a1767f0:g:xWwAAOSwmEJj5GR0&itmprp=enc%3AAQAKAAAA0FkggFvd1GGDu0w3yXCmi1eKagTGaTrWWelWsT5zm%2FP%2FY7ELd3CHZM4Z8PQUDXfnLWYS82JRBNnw6Cswur3TO0%2BEAHxFhsGd2wv8A%2Bqwr%2FLovE%2B5ke4pfMcNpVE1VT0wP0jw6b6EREz8DoYoS0aDAtAKBvX4HmI3q9yjK4pOKZZCJxqMKWmrCVSd7%2FTAsi92kY5Dp8ebGdcPwqDmyIi7k%2FZT7LOeMsFS6g3IU%2FCcyodZYnGwCiO3%2BVlMfHxoxPWBQzzADSGP91OoQ9vRr5KK%2Bc0%3D%7Ctkp%3ABk9SR_it3JXiZQ",
        "https://www.ebay.com/itm/405899323538?_skw=children+toys&itmmeta=01JW8NQ2V64MCXJWVR0SW6WQA4&hash=item5e817c2892:g:gJYAAOSwvoRoNDjC&itmprp=enc%3AAQAKAAAA8FkggFvd1GGDu0w3yXCmi1dTQIbC2uPklgqVEwrdjA2jzdB65Xb0MEnuGikRKLDgFr2yzpwKme2zfJFWVYedPL1Stfsw2NT%2FpGdLF4hfuLC0Y%2BJKvVpTuT3beJih%2FICj7vtST7chC3S2B9AGSlPy5W0jOpPqh6%2Beq4C87%2ByhnO8IeAs%2BeDwxsnmtvNfUzEOElgXkJNqhPKemNcg%2Brtjvk37N2ieSaFBGJswDiysX3e75gKmGW05adFSdBPsBmUTEmZFG2iPDhv0jSZopVd1%2BjglP6CP65i0ZZv4Boof0k8BxfWkuWQxAfsd9XFg65N%2F0iw%3D%3D%7Ctkp%3ABk9SR_it3JXiZQ",
        "https://www.ebay.com/itm/395441644768?_skw=children+toys&itmmeta=01JW8NQ2V668J214J5J58DZ4VZ&hash=item5c1228a4e0:g:H2YAAOSw9lhmWv0M&itmprp=enc%3AAQAKAAAA0FkggFvd1GGDu0w3yXCmi1ccR6rQT5ow2tyYiWI843OJU37ut6mce7El3rM6qKRcDOest8dyKbesy0BWagjVGRh9C7kuZjxrAF4el2HFu8xtwW0nCPwYkbjxFLafyIaBjSLV8hAItdViDHf8%2BvqFRcnE0pmrW16zGnGZ3tYCQmZ7s6O6fd%2B1TVLZ%2BxZflWweF7qb4XuEpE0M5P6apZoMbV2y%2FuO1K0okB0tM%2BMSukZaSizi%2BMitRnPbkxzkshEV6u7wol%2B5bP4G8HgDn72pDv8c%3D%7Ctkp%3ABk9SR_it3JXiZQ",
        "https://www.ebay.com/itm/314681367295?_skw=children+toys&itmmeta=01JW8NQ2V6NB557C40RAXWKVBJ&hash=item4944789aff:g:YjYAAOSwcVBkn1tM&itmprp=enc%3AAQAKAAAA0FkggFvd1GGDu0w3yXCmi1dZN3P063WGnhVHIZC5uXBRmCu%2Bm3hdBGPrYQ0llvaiS9AHU3D3P4YS82nxAW9qRbnXHCbDKrEFuB6zengAgqFamE8qYNf7wCB2b%2F6%2FsTdNje0Zdlo%2F4U9t1D%2F6CoqGeyCN%2FyY6QZHnaDcRioGcjAHO%2FNmDJEM1%2F4Zjm119Vah%2FXTtnDFzejbyMrYj2IYe756pIeX4VJALTHsQ8dmj56n2dZxpj6%2BPNgSv0VR5YCdueJY3Su0YIkJHf5OmGTVH%2Bq1M%3D%7Ctkp%3ABk9SR_it3JXiZQ",
        "https://www.ebay.com/itm/356273857949?_skw=children+toys&itmmeta=01JW8NQ2V6NXQNG6MC7ZDDYBG8&hash=item52f393a59d:g:6jIAAOSwFiRnOrLe&itmprp=enc%3AAQAKAAAA8FkggFvd1GGDu0w3yXCmi1capbuwUFXcbSau1wrHKqXLR409HvF7Hq%2F7jmtDzNtbp4AzLyAPrS6PST1g6tbuJOl3tgK9f5JXnkCvL8rzAx1xMn4qauxzQazV4Yael28Ya0C5JeztLJ8fw757E2VrTXDgmDViNZhTU6RLTFXV11NAeFqGZ%2BmDBQbeBarkVGjlA9rY7Cm9GreusNaqYHV3LDB6SValoPTFszYDGM3rop1Q8WcIJPcPMnaDfTLXdizU8OurqreK%2Bff7%2BjV7jiyI4kvLBsDiEETkhekF9n5eUhmGCoNmE0HoqhSOCEL8IDAAzQ%3D%3D%7Ctkp%3ABk9SR_it3JXiZQ"
        # ... diğer 98 link ...
    ]

    # Örümcek için özel ayarlar (isteğe bağlı ama önerilir)
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        # Genel bir tarayıcı User-Agent'ı
        'DOWNLOAD_DELAY': 2,  # Her istek arasında 2 saniye bekle (eBay'i yormamak için)
        'AUTOTHROTTLE_ENABLED': True,  # Otomatik yavaşlatma/hızlandırma
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,  # Aynı anda tek bir istek
        'ROBOTSTXT_OBEY': True,  # eBay'in robots.txt kurallarına uy
        # Eğer Zyte API kullanmak isterseniz (önceki konuşmalarımızdaki gibi):
        # "DOWNLOADER_MIDDLEWARES": {
        #    "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        # },
        # "ZYTE_API_KEY": "YENI_ZYTE_API_ANAHTARINIZ",
        # "ZYTE_API_ENABLED": True,
        # "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",
        # "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        # "ZYTE_API_DEFAULT_PARAMS": {
        #     "browserHtml": True,
        #     "geolocation": "US", # eBay.com için US iyi bir başlangıç olabilir
        #     "httpResponseBody": True,
        # }
    }

    def start_requests(self):
        self.log(f"<<<<< {self.name.upper()} BAŞLIYOR! >>>>>")
        for url in self.start_urls:
            # Eğer Zyte API kullanıyorsanız meta parametresini ekleyebilirsiniz:
            # meta = {
            #     "zyte_api": {
            #         "browserHtml": True,
            #         "geolocation": "US", # veya TR
            #         "httpResponseBody": True,
            #     }
            # }
            # yield scrapy.Request(url, callback=self.parse, meta=meta)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        self.log(f"Sayfa işleniyor: {response.url} - Durum: {response.status}")

        # Eğer Zyte API ve browserHtml kullanıyorsanız, asıl içerik 'browserHtml' içinde olabilir.
        # Bu durumda response'u ona göre ayarlamanız gerekebilir.
        # Şimdilik standart Scrapy yanıtı üzerinden gidiyoruz.

        # *** DİKKAT: Aşağıdaki CSS seçicileri eBay'in sayfa yapısına göre örnektir. ***
        # *** Bu seçiciler zamanla değişebilir ve sizin bunları eBay sayfasını inceleyerek ***
        # *** (tarayıcıda "İncele" veya "Inspect Element" ile) DOĞRULAMANIZ/GÜNCELLEMENİZ gerekir. ***

        # Ürün Başlığı
        # Örnek seçici: eBay'de ürün başlığı genellikle 'h1' içinde ve belirli bir class ile bulunur.
        # Örneğin: 'h1.x-item-title__mainTitle span.ux-textspans'
        title = response.css('h1.x-item-title__mainTitle span.ux-textspans::text').get()
        if not title:  # Bazen başlık farklı bir yapıda olabilir
            title = response.css('h1#itemTitle::text').get()  # Eski bir yapı örneği
        if title:
            title = title.strip()

        # Ürün Fiyatı
        # Örnek seçici: Fiyat 'div.x-price-primary span.ux-textspans' gibi bir yerde olabilir.
        price_text = response.css('div.x-price-primary span.ux-textspans::text').get()
        if not price_text:  # Bazen fiyat farklı bir yapıda olabilir
            price_text = response.css('span#prcIsum::text').get()  # Eski bir yapı örneği
            if not price_text:
                price_text = response.css('span[itemprop="price"]::attr(content)').get()  # Meta etiketinden fiyat

        price = None
        if price_text:
            price = price_text.strip()
            # Fiyattaki para birimi simgesini ve virgülleri temizlemek gerekebilir
            # price = price.replace('$', '').replace('€', '').replace('£', '').replace('TL', '').replace(',', '').strip()

        # Diğer Detaylar (Örnekler - Kendi İhtiyaçlarınıza Göre Çoğaltın)
        # Satıcı Bilgisi
        # seller_info = response.css('div.x-sellercard-atf__info__about-seller a.ux-textspans--PSEUDOLINK span.ux-textspans::text').get()
        # if seller_info:
        #     seller_info = seller_info.strip()

        # Ürün Durumu (Condition)
        # condition = response.css('div.x-item-condition-text span.ux-textspans::text').get()
        # if condition:
        #     condition = condition.strip()

        # Resim URL'si
        # image_url = response.css('div.ux-image-carousel-item.active img::attr(src)').get()
        # if not image_url:
        #     image_url = response.css('img#icImg::attr(src)').get()

        self.log(f"Başlık: {title}, Fiyat: {price}")

        yield {
            'url': response.url,
            'title': title,
            'price': price,
            # 'seller': seller_info,
            # 'condition': condition,
            # 'image_url': image_url,
            # ... diğer ayıklamak istediğiniz veriler ...
        }