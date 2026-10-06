import sys
from scraper.client import HttpClient
from scraper.parser import ProductParser
from scraper.storage import DataStorage
from scraper.utils import farsi

TARGET_URL = "https://www.technolife.ir/product/list/164_163_130/"
TOTAL_PAGES = 1

def run():
    print(farsi("شروع فرآیند استخراج خودکار..."))
    client = HttpClient()
    all_products = []

    for page in range(1, TOTAL_PAGES + 1):
        url = f"{TARGET_URL}?page={page}" if page > 1 else TARGET_URL
        html = client.fetch_html(url)
        if html:
            products = ProductParser.parse_product_list(html)
            all_products.extend(products)

        if all_products:
            storage = DataStorage()
            storage.save_to_json(all_products, "technolife_products.json")
            print(farsi(f"عملیات موفق: {len(all_products)} محصول ذخیره شد."))
            sys.exit(0)
        else:
            print(farsi("خطا: دیتایی دریافت نشد."))
            sys.exit(1)

if __name__ == "__main__":
    run()
