import sys
from pathlib import Path
from scraper.client import DigikalaClient
from scraper.parser import DigikalaParser
from scraper.storage import DataStorage
from scraper.utills import farsi

def run(keyword: str = "کتاب اثر مرکب", page: int = 1):
    print(farsi(f"شروع استخراج اطلاعات برای کلیدواژه: '{keyword}' - صفحه {page}"))
    
    # 1. دریافت داده خام
    client = DigikalaClient()
    raw_data = client.fetch_search_results(keyword=keyword, page=page)
    
    # 2. پارس و ساختاردهی داده‌ها
    parsed_products = DigikalaParser.parse_search_results(raw_data)
    total = len(parsed_products)
    print(farsi(f"تعداد {total} محصول با موفقیت استخراج شد."))
    
    if not parsed_products:
        print(farsi("داده‌ای برای ذخیره‌سازی یافت نشد."))
        return

    # 3. ذخیره‌سازی خروجی
    storage = DataStorage(output_dir="data")
    filename = f"products_{keyword.replace(' ', '_')}_p{page}"
    
    csv_file = storage.save_to_csv(parsed_products, filename)
    json_file = storage.save_to_json(parsed_products, filename)
    
    print(farsi(f"گزارش CSV ذخیره شد: {csv_file}"))
    print(farsi(f"گزارش JSON ذخیره شد: {json_file}"))
    print(farsi("عملیات با موفقیت پایان یافت."))


if __name__ == "__main__":
    run(keyword="کتاب اثر مرکب", page=1)
