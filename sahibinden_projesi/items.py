# sahibinden_projesi/items.py
import scrapy

class EbayProductItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    # seller = scrapy.Field()
    # condition = scrapy.Field()
    # image_url = scrapy.Field()
    # ... eklemek istediğiniz diğer alanlar ...