# settings.py
BOT_NAME = "sahibinden_projesi"

SPIDER_MODULES = ["sahibinden_projesi.spiders"]
NEWSPIDER_MODULE = "sahibinden_projesi.spiders"

# Obey robots.txt rules - Örümcek içinde yönetildiği için bunu kaldırıyoruz veya False yapıyoruz.
ROBOTSTXT_OBEY = False

# Diğer varsayılan ayarlarınız burada kalabilir...

# Zyte API için gerekli olan bu ayarları örümcek içinde
# yönetmek yerine buraya da ekleyebiliriz. Ama şimdilik
# custom_settings'de bırakmak daha net olabilir.
# Eğer buraya eklerseniz, örümcekten kaldırabilirsiniz.
#
# ZYTE_API_KEY = "bf2eb06c893e488f9eddf6f33ed87477" # <-- Güvenlik için bunu Scrapy Cloud ayarlarından yapmak en iyisi!
# ZYTE_API_ENABLED = True
# DOWNLOADER_MIDDLEWARES = {
#    "scrapy_zyte_api.ScrapyZyteAPIDownloaderMiddleware": 1000,
# }
# REQUEST_FINGERPRINTER_CLASS = "scrapy_zyte_api.ScrapyZyteAPIRequestFingerprinter"
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# HTTPERROR_ALLOWED_CODES = [403]

FEED_EXPORT_ENCODING = "utf-8"