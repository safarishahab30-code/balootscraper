from scraper.client import DigikalaClient
from scraper.storage import DataStorage
from scraper.utils import farsi
from scraper.parser import ProductParser


def run_scraper(keyword: str, total_pages: int = 1):
    client = DigikalaClient()
    storage = DataStorage()

    all_products = []

    for page in range(1, total_pages + 1):
        print(farsi(f"در حال دریافت اطلاعات صفحه {page} برای کلیدواژه '{keyword}'..."))
        raw_data = client.fetch_search_results(keyword=keyword, page=page)

        if not raw_data:
            print(farsi(f"پاسخی برای صفحه {page} دریافت نشد."))
            break
        
        # اصلاح: استفاده از raw_data و مقداردهی مستقیم به products
        products = ProductParser.parse_search_results(raw_data)
        
        if not products:
            print(farsi(f"محصولی در صفحه {page} یافت نشد."))
            break

        all_products.extend(products)
        print(farsi(f"صفحه {page}: تعداد {len(products)} محصول دریافت شد."))

    if not all_products:
        print(farsi("هیچ داده‌ای برای ذخیره‌سازی یافت نشد."))
        return

    clean_keyword = keyword.replace(" ", "_")
    base_filename = f"products_{clean_keyword}_pages_{total_pages}"

    csv_path = storage.save_to_csv(all_products, base_filename)
    json_path = storage.save_to_json(all_products, base_filename)
    excel_path = storage.save_to_excel(all_products, base_filename)

    print(farsi(f"مجموع کل محصولات استخراج شده: {len(all_products)}"))
    print(farsi(f"گزارش CSV: {csv_path}"))
    print(farsi(f"گزارش JSON: {json_path}"))
    print(farsi(f"گزارش Excel: {excel_path}"))
    print(farsi("عملیات با موفقیت پایان یافت."))


if __name__ == "__main__":
    run_scraper(keyword="کتاب اثر مرکب", total_pages=2)
