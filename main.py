import os
import argparse
from dotenv import load_dotenv

from scraper.client import HttpClient
from scraper.storage import DataStorage
from scraper.parser import ProductParser
from scraper.utils import farsi

load_dotenv()


def run_scraper(total_pages: int = 1):
    """پایپ‌لاین استخراج محصولات موبایل از تکنولایف"""
    client = HttpClient()
    storage = DataStorage()
    url = "https://www.technolife.ir/product/list/69_70_79/تمامی-گوشی%E2%80%8Cها"
    all_products = []

    for page in range(1, total_pages + 1):
        print(farsi(f"در حال دریافت صفحه {page}..."))
        html_content = client.fetch_html(url)

        if not html_content:
            print(farsi(f"محتوای صفحه {page} دریافت نشد."))
            break

        products = ProductParser.parse_product_list(html_content)
        if not products:
            print(farsi(f"محصولی در صفحه {page} یافت نشد."))
            break

        all_products.extend(products)
        print(farsi(f"صفحه {page}: تعداد {len(products)} محصول استخراج شد."))

    if not all_products:
        print(farsi("هیچ داده‌ای برای ذخیره‌سازی یافت نشد."))
        return

    base_filename = "technolife_mobiles"
    csv_path = storage.save_to_csv(all_products, base_filename)
    json_path = storage.save_to_json(all_products, base_filename)
    excel_path = storage.save_to_excel(all_products, base_filename)

    print(farsi(f"مجموع کل محصولات استخراج شده: {len(all_products)}"))
    print(farsi(f"گزارش CSV: {csv_path}"))
    print(farsi(f"گزارش JSON: {json_path}"))
    print(farsi(f"گزارش Excel: {excel_path}"))
    print(farsi("عملیات استخراج با موفقیت پایان یافت."))


def run_engine():
    """موتور مشاوره هوش مصنوعی (اختیاری)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(farsi("خطا: کلید GROQ_API_KEY در فایل .env تعریف نشده است."))
        return

    try:
        from scraper.ai import BookAIAssistant
    except ImportError:
        print(farsi("ماژول scraper/ai.py یافت نشد. موتور AI در دسترس نیست."))
        return

    ai_assistant = BookAIAssistant(api_key=api_key)
    print(farsi("موتور هوش مصنوعی بارگذاری شد. (جهت خروج 'exit' را وارد کنید)"))

    while True:
        user_query = input(farsi("پرسش شما: "))
        if user_query.strip().lower() in ["exit", "خروج"]:
            print(farsi("خروج از سامانه."))
            break
        response = ai_assistant.get_recommendation(user_query)
        print(farsi(f"پاسخ سیستم: {response}"))


def main():
    parser = argparse.ArgumentParser(description=farsi("موتور رصد قیمت و استخراج محصولات"))
    parser.add_argument("--pages", type=int, default=1, help=farsi("تعداد صفحات برای اسکرپ (پیش‌فرض: 1)"))
    parser.add_argument("--chat", action="store_true", help=farsi("اجرای موتور هوش مصنوعی به صورت تعاملی"))
    args = parser.parse_args()

    if args.chat:
        run_engine()
    else:
        run_scraper(args.pages)


if __name__ == "__main__":
    main()
