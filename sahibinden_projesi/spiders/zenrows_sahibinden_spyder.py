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
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except NameError:
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
    allowed_domains = ['sahibinden.com']

    ZENROWS_API_KEY = "67129c0a63f61c085f3d9bea1105129f0cdfa59e"  # TODO: Scrapy settings veya env variable'dan okuyun
    ZENROWS_WAIT_TIME = "5000"
    REQUEST_DELAY = 1

    custom_settings = {
        'RETRY_TIMES': 2,  # Hata durumunda yeniden deneme sayısı
        'DOWNLOAD_DELAY': REQUEST_DELAY,
        'DOWNLOAD_TIMEOUT': 180,
        'LOG_LEVEL': 'INFO',  # Daha fazla detay için 'DEBUG' yapabilirsiniz
        # 'DUPEFILTER_DEBUG': True, # Yinelenen filtreleme hatalarını ayıklamak için
    }

    def __init__(self, *args, **kwargs):
        super(SahibindenSpider, self).__init__(*args, **kwargs)
        try:
            # API anahtarını settings'den almayı deneyin, yoksa hardcoded değeri kullanın
            self.actual_api_key = getattr(self.settings, 'ZENROWS_API_KEY', self.ZENROWS_API_KEY)
            if not self.actual_api_key:
                raise ValueError("ZenRows API anahtarı bulunamadı veya boş.")
            self.zenrows_client = ZenRowsClient(self.actual_api_key)
            self.logger.info("ZenRowsClient başarıyla başlatıldı.")
        except Exception as e:
            self.logger.error(f"ZenRowsClient başlatılırken hata oluştu: {e}", exc_info=True)
            # Eğer client başlatılamazsa, spider'ı durdurmak daha iyi olabilir
            # raise e
            self.zenrows_client = None  # Hatalı durumda client'ı None yap

        self.params = {
            "js_render": "true",
            "premium_proxy": "true",
            "proxy_country": "tr",
            "wait": self.ZENROWS_WAIT_TIME
        }
        self.all_csv_headers = self._initialize_csv_headers()
        self.logger.info(f"CSV başlıkları {len(self.all_csv_headers)} adet olarak oluşturuldu.")

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
        self.logger.info(f"Giriş CSV dosyası okunuyor: {INPUT_CSV_PATH}")
        if not os.path.exists(INPUT_CSV_PATH):
            self.logger.error(f"Giriş CSV dosyası bulunamadı: {INPUT_CSV_PATH}")
            with open(INPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ilan_id', 'link'])
                writer.writerow(['ÖRNEK_ID_1',
                                 'https://www.sahibinden.com/ilan/vasita-otomobil-volkswagen-ornek-ilan-linki-1-123456789/detay'])
            self.logger.info(
                f"Örnek bir '{os.path.basename(INPUT_CSV_PATH)}' dosyası oluşturuldu. Lütfen ilanları ekleyin ve tekrar çalıştırın.")
            return

        try:
            with open(INPUT_CSV_PATH, mode='r', newline='', encoding='utf-8') as infile:
                self.logger.info(f"'{INPUT_CSV_PATH}' başarıyla açıldı.")
                # Dosyanın boş olup olmadığını kontrol et
                first_line = infile.readline()
                if not first_line:
                    self.logger.warning(f"'{INPUT_CSV_PATH}' dosyası boş.")
                    return
                infile.seek(0)  # Dosya işaretçisini başa al

                reader = csv.DictReader(infile)
                if not reader.fieldnames or 'ilan_id' not in reader.fieldnames or 'link' not in reader.fieldnames:
                    self.logger.error(
                        f"'{os.path.basename(INPUT_CSV_PATH)}' dosyasında 'ilan_id' ve 'link' sütunları bulunmalıdır veya dosya başlık satırı eksik/hatalı. Bulunan başlıklar: {reader.fieldnames}")
                    return

                self.logger.info(f"CSV başlıkları bulundu: {reader.fieldnames}")
                request_count = 0
                for i, row in enumerate(reader):
                    self.logger.debug(f"CSV satırı {i + 1} işleniyor: {row}")
                    ilan_id = row.get('ilan_id', '').strip()
                    url = row.get('link', '').strip()
                    if ilan_id and url:
                        self.logger.info(f"İstek oluşturuluyor: ID {ilan_id}, URL {url}")
                        yield scrapy.Request(
                            url,
                            callback=self.parse,
                            meta={'ilan_id': ilan_id, 'original_url': url},
                            dont_filter=True,  # Eğer CSV'de aynı URL birden fazla kez varsa hepsini işle
                            cb_kwargs={'ilan_id_arg': ilan_id, 'original_url_arg': url}
                        )
                        request_count += 1
                    else:
                        self.logger.warning(f"Eksik ilan_id veya link (satır {i + 1}): {row} - Atlanıyor.")

                if request_count == 0:
                    self.logger.warning(f"İşlenecek geçerli link bulunamadı: {INPUT_CSV_PATH}")

        except FileNotFoundError:
            self.logger.error(f"Giriş CSV dosyası (FileNotFoundError ile tekrar yakalandı): {INPUT_CSV_PATH}")
        except Exception as e:
            self.logger.error(f"Giriş CSV okunurken veya istek oluşturulurken genel hata: {e}", exc_info=True)

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
        except Exception as e:
            self.logger.debug(f"XPath '{xpath_expression}' ile metin çıkarılırken hata: {e}")
            return default

    def extract_list_by_xpath(self, tree, xpath_expression):
        try:
            elements = tree.xpath(xpath_expression)
            return [el.text_content().strip() for el in elements if el.text_content() and el.text_content().strip()]
        except Exception as e:
            self.logger.debug(f"XPath '{xpath_expression}' ile liste çıkarılırken hata: {e}")
            return []

    def parse(self, response, ilan_id_arg, original_url_arg):
        if not self.zenrows_client:
            self.logger.error(f"ZenRowsClient başlatılamadığı için ID {ilan_id_arg} işlenemiyor.")
            item_error = {'ilan_id': ilan_id_arg, 'link': original_url_arg,
                          'hata_durumu': 'ZenRowsClient başlatılamadı'}
            yield item_error
            return

        self.logger.info(f"ZenRows ile sayfa çekiliyor: ID {ilan_id_arg}, URL: {original_url_arg}")
        item = {k: '' for k in self.all_csv_headers}
        item['ilan_id'] = ilan_id_arg
        item['link'] = original_url_arg
        item['kayit_tarihi'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        try:
            zenrows_response = self.zenrows_client.get(original_url_arg, params=self.params)
            zenrows_response.raise_for_status()
            html_content = zenrows_response.text
            tree = html.fromstring(html_content)
            self.logger.debug(f"Sayfa başarıyla çekildi ve parse edildi: ID {ilan_id_arg}")

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
                        self.logger.warning(
                            f"Bilinmeyen ilan detayı (CSV başlıklarında yok): {key_raw} -> {value} (ID: {ilan_id_arg})")

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
                                if feature_slug in item:
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

            self.logger.info(f"Veri başarıyla çekildi ve yield ediliyor: ID {ilan_id_arg}")
            yield item

        except Exception as e:
            self.logger.error(
                f"Sayfa parse edilirken veya ZenRows isteği sırasında hata: ID {ilan_id_arg}, URL: {original_url_arg}, Hata: {e}",
                exc_info=True)
            item['hata_durumu'] = str(e)
            yield item
