# -*- coding: utf-8 -*-
import scrapy
from lxml import html
import csv
import os
from datetime import datetime
import re
import time
from zenrows import ZenRowsClient  # ZenRowsClient'ı import ediyoruz

# Spider'ın çalışacağı dizini belirle (ilan_linkleri.csv için)
# Scrapy Cloud'da bu dosyanın projenin kök dizininde olması beklenir.
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:  # __file__ interaktif modda tanımlı değilse
    BASE_DIR = os.getcwd()
INPUT_CSV_PATH = os.path.join(BASE_DIR, 'ilan_linkleri.csv')


def slugify(text):
    if not text: return ""
    text = text.lower()
    text = re.sub(r'\s+ve\s+|\s+&\s+', '_ve_', text)
    text = re.sub(r'\s*/\s*', '_', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text).strip('_')
    replacements = {'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


# Bilinen özellik kategorileri ve maddeleri (GLOBAL KAPSAMDA)
KNOWN_FEATURE_CATEGORIES = {
    "Güvenlik": ["ABS", "AEB", "BAS", "Çocuk Kilidi", "Distronic", "ESP / VSA", "Gece Görüş Sistemi",
                 "Hava Yastığı (Sürücü)", "Hava Yastığı (Yolcu)", "Immobilizer", "Isofix", "Kör Nokta Uyarı Sistemi",
                 "Merkezi Kilit", "Şerit Takip Sistemi", "Yokuş Kalkış Desteği", "Yorgunluk Tespit Sistemi",
                 "Zırhlı Araç"],
    "İç Donanım": ["Hidrolik Direksiyon", "Üçüncü Sıra Koltuklar", "Deri Koltuk", "Kumaş Koltuk", "Elektrikli Camlar",
                   "Klima", "Otm.Kararan Dikiz Aynası", "Ön Görüş Kamerası", "Ön Koltuk Kol Dayaması",
                   "Anahtarsız Giriş ve Çalıştırma", "Fonksiyonel Direksiyon", "Isıtmalı Direksiyon",
                   "Koltuklar (Elektrikli)", "Koltuklar (Hafızalı)", "Koltuklar (Isıtmalı)", "Koltuklar (Soğutmalı)",
                   "Hız Sabitleme Sistemi", "Soğutmalı Torpido", "Yol Bilgisayarı", "Head-up Display", "Start / Stop",
                   "Geri Görüş Kamerası"],
    "Dış Donanım": ["Ayakla Açılan Bagaj Kapağı", "Hardtop", "Far (Adaptif)", "Aynalar (Elektrikli)",
                    "Aynalar (Isıtmalı)", "Aynalar (Hafızalı)", "Park Sensörü (Arka)", "Park Sensörü (Ön)",
                    "Park Asistanı", "Sunroof", "Akıllı Bagaj Kapağı", "Panoramik Cam Tavan", "Römork Çeki Demiri"],
    "Multimedya": ["Android Auto", "Apple CarPlay", "Bluetooth", "USB / AUX"]
}


class SahibindenSpider(scrapy.Spider):
    name = 'sahibinden_detail_scraper'
    allowed_domains = ['sahibinden.com']  # ZenRows proxy üzerinden gidileceği için bu çok kritik olmayabilir

    # Scrapy Cloud'da API anahtarını settings veya environment variable olarak ayarlamak daha iyidir.
    # settings.py dosyanıza ekleyebilirsiniz: ZENROWS_API_KEY = "YOUR_API_KEY"
    # Ya da Scrapy Cloud projenizin environment variable'larına ekleyebilirsiniz.
    # Bu örnekte doğrudan kullanıyoruz, ancak canlı ortamda değiştirin.
    ZENROWS_API_KEY = "67129c0a63f61c085f3d9bea1105129f0cdfa59e"
    ZENROWS_WAIT_TIME = "5000"  # Milisaniye
    REQUEST_DELAY = 1  # Saniye

    custom_settings = {
        'RETRY_TIMES': 3,
        'DOWNLOAD_DELAY': REQUEST_DELAY,  # Her istek arasında genel bir gecikme
        # ZenRows için daha uzun timeout gerekebilir
        'DOWNLOAD_TIMEOUT': 180,
    }

    def __init__(self, *args, **kwargs):
        super(SahibindenSpider, self).__init__(*args, **kwargs)
        self.zenrows_client = ZenRowsClient(self.ZENROWS_API_KEY)
        self.params = {
            "js_render": "true",
            "premium_proxy": "true",  # Planınıza göre ayarlayın
            "proxy_country": "tr",
            "wait": self.ZENROWS_WAIT_TIME
            # "antibot": "true", # Gerekirse ZenRows'un antibot özelliklerini kullanın
            # "js_instructions": "[{\"click\":\"#some_button\"}, {\"wait_for\":\"#some_element\"}]" # İleri düzey JS etkileşimleri
        }
        self.all_csv_headers = self._initialize_csv_headers()

    def _initialize_csv_headers(self):
        base_headers = [
            'kayit_tarihi', 'ilan_id', 'link', 'ilan_basligi', 'fiyat', 'konum',
            'ilan_no_detay', 'ilan_tarihi_detay', 'marka', 'seri', 'model', 'yil',
            'yakit_tipi', 'vites', 'arac_durumu', 'km', 'kasa_tipi', 'motor_gucu',
            'motor_hacmi', 'cekis', 'renk', 'garanti', 'agir_hasar_kayitli',
            'plaka_uyruk', 'kimden', 'takas', 'satici_magaza_adi', 'satici_adi',
            'satici_telefonu', 'aciklama',
            'lokal_boyali_parcalar', 'boyali_parcalar', 'degisen_parcalar'
        ]
        dynamic_feature_headers = []
        for category_title, features in KNOWN_FEATURE_CATEGORIES.items():
            cat_slug = slugify(category_title)
            for feature in features:
                dynamic_feature_headers.append(f"{cat_slug}_{slugify(feature)}")
        return base_headers + sorted(list(set(dynamic_feature_headers)))

    def start_requests(self):
        # ilan_linkleri.csv dosyasını oku
        # Bu dosyanın Scrapy projenizin ana dizininde olduğunu varsayıyoruz.
        # Scrapy Cloud'a deploy ederken bu dosyayı da projenize dahil etmelisiniz.

        if not os.path.exists(INPUT_CSV_PATH):
            self.logger.error(f"Giriş CSV dosyası bulunamadı: {INPUT_CSV_PATH}")
            # Örnek bir ilan_linkleri.csv dosyası oluşturabilirsiniz
            with open(INPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ilan_id', 'link'])
                writer.writerow(['ÖRNEK_ID_1',
                                 'https://www.sahibinden.com/ilan/vasita-otomobil-volkswagen-ornek-ilan-linki-1-123456789/detay'])
            self.logger.info(
                f"Örnek bir '{os.path.basename(INPUT_CSV_PATH)}' dosyası oluşturuldu. Lütfen ilanları ekleyin.")
            return

        try:
            with open(INPUT_CSV_PATH, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                if 'ilan_id' not in reader.fieldnames or 'link' not in reader.fieldnames:
                    self.logger.error(
                        f"'{os.path.basename(INPUT_CSV_PATH)}' dosyasında 'ilan_id' ve 'link' sütunları bulunmalıdır.")
                    return

                for row in reader:
                    ilan_id = row.get('ilan_id', '').strip()
                    url = row.get('link', '').strip()
                    if ilan_id and url:
                        # ZenRows üzerinden istek yapmak için meta kullanacağız
                        # Scrapy'nin kendi request mekanizması yerine ZenRows'u kullanacağız.
                        # Bu nedenle, doğrudan bir URL'ye istek atmıyoruz, parse metodunda ZenRows'u çağıracağız.
                        # `cb_kwargs` ile parse metoduna ekstra argümanlar geçebiliriz.
                        yield scrapy.Request(url, self.parse, meta={'ilan_id': ilan_id, 'original_url': url},
                                             dont_filter=True,
                                             cb_kwargs={'ilan_id_arg': ilan_id, 'original_url_arg': url})
                    else:
                        self.logger.warning(f"Eksik ilan_id veya link: {row} - Atlanıyor.")
        except FileNotFoundError:
            self.logger.error(f"Giriş CSV dosyası bulunamadı: {INPUT_CSV_PATH}")
        except Exception as e:
            self.logger.error(f"Giriş CSV okunurken hata: {e}")

    def extract_text_by_xpath(self, tree, xpath_expression, default="Bulunamadı", join_multi=False, separator=" "):
        try:
            elements = tree.xpath(xpath_expression)
            if elements:
                if join_multi:
                    return separator.join(el.text_content().strip() for el in elements if
                                          el.text_content() and el.text_content().strip()).strip()
                if isinstance(elements[0], html.HtmlElement):
                    return elements[0].text_content().strip()
                else:
                    return str(elements[0]).strip()
            return default
        except Exception:
            return default

    def extract_list_by_xpath(self, tree, xpath_expression):
        try:
            elements = tree.xpath(xpath_expression)
            return [el.text_content().strip() for el in elements if el.text_content() and el.text_content().strip()]
        except Exception:
            return []

    def parse(self, response, ilan_id_arg, original_url_arg):
        self.logger.info(f"Sayfa çekiliyor: ID {ilan_id_arg}, URL: {original_url_arg}")
        item = {k: '' for k in self.all_csv_headers}  # Tüm başlıklar için varsayılan boş değerler
        item['ilan_id'] = ilan_id_arg
        item['link'] = original_url_arg
        item['kayit_tarihi'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        try:
            # ZenRows ile sayfa içeriğini al
            # Scrapy'nin response'u yerine ZenRows response'unu kullanacağız
            zenrows_response = self.zenrows_client.get(original_url_arg, params=self.params)
            zenrows_response.raise_for_status()  # HTTP hatalarını kontrol et
            html_content = zenrows_response.text
            tree = html.fromstring(html_content)

            # Veri Ayıklama (Mevcut XPath mantığınızı buraya entegre edin)
            item['ilan_basligi'] = self.extract_text_by_xpath(tree, "//div[@class='classifiedDetailTitle']/h1/text()")
            fiyat_str = self.extract_text_by_xpath(tree,
                                                   "//div[contains(@class,'classifiedInfo')]/h3/span[@class='classified-price-wrapper']/text()")
            item['fiyat'] = fiyat_str if fiyat_str != "Bulunamadı" else "Fiyat bulunamadı"

            konum_parts = tree.xpath("//div[contains(@class,'classifiedInfo')]/h2//a/text()")
            item['konum'] = " / ".join([part.strip() for part in konum_parts]) if konum_parts else "Konum bulunamadı"

            details_ul = tree.xpath("//ul[@class='classifiedInfoList']/li")
            for li in details_ul:
                key_element = li.xpath("./strong/text()")
                value_element = li.xpath("./span/text()")
                if key_element and value_element:
                    key_raw = key_element[0].strip()
                    value = value_element[0].strip()
                    key_slug = slugify(key_raw)

                    if key_raw == 'İlan No':
                        item['ilan_no_detay'] = value
                    elif key_raw == 'İlan Tarihi':
                        item['ilan_tarihi_detay'] = value
                    elif key_raw == 'Plaka / Uyruk':
                        item['plaka_uyruk'] = value
                    elif key_slug in self.all_csv_headers:
                        item[key_slug] = value
                    else:
                        self.logger.warning(f"Bilinmeyen ilan detayı: {key_raw} -> {value} (ID: {ilan_id_arg})")

            item['satici_magaza_adi'] = self.extract_text_by_xpath(tree,
                                                                   "//div[contains(@class, 'user-info-module')]//div[@class='user-info-store-name']/a/text()",
                                                                   "Mağaza adı bulunamadı")
            item['satici_adi'] = self.extract_text_by_xpath(tree,
                                                            "//div[contains(@class, 'user-info-module')]//div[@class='user-info-agent']/h3/text()",
                                                            "Satıcı adı bulunamadı")

            phone_info_parts = []
            phone_dl_groups = tree.xpath(
                "//div[contains(@class, 'user-info-module')]//div[@class='user-info-phones']//div[@class='dl-group']")
            for group in phone_dl_groups:
                phone_type_list = group.xpath("./dt/text()")
                phone_type = phone_type_list[0].strip() if phone_type_list else "Bilinmeyen Tip"
                number_str = "Bulunamadı"
                data_content_numbers = group.xpath("./dd/span/@data-content")
                if data_content_numbers:
                    number_str = data_content_numbers[0].strip()
                else:
                    direct_dd_text_list = group.xpath("./dd/text()")
                    if direct_dd_text_list and direct_dd_text_list[0].strip():
                        number_str = direct_dd_text_list[0].strip().splitlines()[0]
                    else:
                        all_dd_text_list = group.xpath("./dd//text()")
                        if all_dd_text_list:
                            full_dd_text = "".join(t.strip() for t in all_dd_text_list if t.strip()).strip()
                            if full_dd_text: number_str = full_dd_text
                if number_str != "Bulunamadı": phone_info_parts.append(f"{phone_type}: {number_str}")
            item['satici_telefonu'] = " | ".join(phone_info_parts) if phone_info_parts else "Telefon bulunamadı"

            aciklama_nodes = tree.xpath("//div[@id='classifiedDescription']//text()")
            aciklama_raw = "".join([node.strip() for node in aciklama_nodes if node.strip()])
            item['aciklama'] = re.sub(r'\n\s*\n+', '\n',
                                      aciklama_raw).strip() if aciklama_raw else "Açıklama bulunamadı"

            properties_base_xpath = "//div[@id='classifiedProperties']"
            properties_container = tree.xpath(properties_base_xpath)
            if properties_container:
                prop_tree = properties_container[0]
                for category_title, features_in_cat in KNOWN_FEATURE_CATEGORIES.items():
                    cat_slug = slugify(category_title)
                    section_h3 = prop_tree.xpath(f"./h3[contains(text(), '{category_title}')]")
                    if section_h3:
                        ul_element = section_h3[0].xpath("./following-sibling::ul[1]")
                        if ul_element:
                            all_li_items = ul_element[0].xpath("./li")
                            for feature_item_text in features_in_cat:
                                feature_slug = f"{cat_slug}_{slugify(feature_item_text)}"
                                if feature_slug in item:  # Başlıkta olduğundan emin ol
                                    for li in all_li_items:
                                        li_text_content = li.text_content().strip()
                                        if li_text_content.startswith(feature_item_text):
                                            if "selected" in li.get("class", ""):
                                                item[feature_slug] = "EVET"
                                            break

            item['lokal_boyali_parcalar'] = ", ".join(self.extract_list_by_xpath(tree,
                                                                                 f"{properties_base_xpath}//div[contains(@class, 'car-damage-info-list')]//ul[li[@class='pair-title local-painted-new']]/li[@class='selected-damage']/text()")) or "Yok"
            item['boyali_parcalar'] = ", ".join(self.extract_list_by_xpath(tree,
                                                                           f"{properties_base_xpath}//div[contains(@class, 'car-damage-info-list')]//ul[li[@class='pair-title painted-new']]/li[@class='selected-damage']/text()")) or "Yok"
            item['degisen_parcalar'] = ", ".join(self.extract_list_by_xpath(tree,
                                                                            f"{properties_base_xpath}//div[contains(@class, 'car-damage-info-list')]//ul[li[@class='pair-title changed-new']]/li[@class='selected-damage']/text()")) or "Yok"

            self.logger.info(f"Veri çekildi: ID {ilan_id_arg}")
            yield item

        except Exception as e:
            self.logger.error(
                f"Sayfa parse edilirken hata oluştu: ID {ilan_id_arg}, URL: {original_url_arg}, Hata: {e}")
            # Hatalı durumu da yield edebiliriz, Scrapy Cloud'da görmek için
            item['hata_durumu'] = str(e)
            yield item

        # Scrapy'nin kendi gecikme mekanizması (DOWNLOAD_DELAY) zaten var,
        # bu yüzden parse sonunda ek bir time.sleep'e genellikle gerek yoktur.
        # Eğer ZenRows tarafında rate limit sorunu yaşarsanız, REQUEST_DELAY'i artırabilir
        # veya ZenRows'un kendi rate limit yönetimine (örneğin, ZenRows planınızdaki concurrency limitleri) güvenebilirsiniz.
