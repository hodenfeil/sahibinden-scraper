import scrapy

class ZyteSahibindenSpider(scrapy.Spider):
    name = "zyte_sahibinden_spider"
    allowed_domains = ["sahibinden.com"]

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
        },
        # ÖNEMLİ: API Anahtarını Scrapy Cloud Ayarlarından (Settings -> Spider Settings)
        # ZYTE_API_KEY olarak eklemek daha güvenlidir. Eğer oradan eklerseniz bu satırı silin.
        # "ZYTE_API_KEY": "bf2eb06c893e488f9eddf6f33ed87477",
        "ZYTE_API_ENABLED": True,

        "REQUEST_FINGERPRINTER_CLASS": "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter",

        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",

        # robots.txt dosyasını dikkate almayı bırak (settings.py'de de False yaptık)
        "ROBOTSTXT_OBEY": False,

        # 403 hatalarını parse metoduna gönder!
        "HTTPERROR_ALLOWED_CODES": [403],
    }

    def start_requests(self):
        """Örümceği başlatan metod."""
        # Dağıtımın başarılı olup olmadığını anlamak için bu log çok önemli!
        self.log("<<<<< YENİ KOD (SÜRÜM 1.3) ÇALIŞIYOR! >>>>>")

        url = "https://www.sahibinden.com/ilan/vasita-otomobil-opel-ilk-ruhsat-sahibinden-alinma-degisensiz-kazasiz-1248665984/detay"

        yield scrapy.Request(
            url,
            callback=self.parse,
            meta={
                "zyte_api": {
                    "browserHtml": True,  # Tarayıcıda aç (403 için önemli)
                    "geolocation": "TR",  # Türkiye'den istek yap
                    "httpResponseBody": True,  # HTML'i al
                }
            }
        )

    def parse(self, response):
        """Gelen yanıtı işleyen metod."""
        self.log(f"Response status: {response.status} for URL: {response.url}")

        if response.status == 403:
            self.log("403 HATASI ALINDI! Sayfa içeriği (ilk 1000 karakter):")
            self.log(response.text[:1000])
            self.log("403 HATASI - SAYFA İÇERİĞİ SONU")
            return

        if response.status == 200:
            self.log("BAŞARILI (200)! Sayfa içeriği (ilk 500 karakter):")
            self.log(response.text[:500])
            self.log("BAŞARILI (200) - SAYFA İÇERİĞİ SONU")
            yield {
                "url": response.url,
                "status": response.status,
                "html": response.text,
            }
        else:
            self.log(f"BEKLENMEDİK DURUM: {response.status}. Sayfa içeriği (ilk 500 karakter):")
            self.log(response.text[:500])