import os
import argparse
from dotenv import load_dotenv

from scraper.client import HttpClient
from scraper.storage import DataStorage
from scraper.parser import ProductParser
from scraper.analyzer import analyze_products
from scraper.utils import farsi


load_dotenv()


# نگاشت برندهای فارسی به اسلاگ استاندارد تکنولایف
BRAND_MAP = {
    "سامسونگ": "samsung",
    "شیائومی": "xiaomi",
    "اپل": "apple",
    "نوکیا": "nokia",
    "هواوی": "huawei",
    "آنر": "honor",
}


def run_scraper(
    total_pages: int = 1,
    brand: str = None,
    min_price: int = None,
    max_price: int = None,
    sort_order: str = None,
    export_format: str = "all",
):
    """پایپ‌لاین استخراج، فیلتر، مرتب‌سازی و ذخیره محصولات موبایل."""

    if total_pages < 1:
        print(farsi("تعداد صفحات باید حداقل ۱ باشد."))
        return

    if min_price is not None and min_price < 0:
        print(farsi("حداقل قیمت نمی‌تواند منفی باشد."))
        return

    if max_price is not None and max_price < 0:
        print(farsi("حداکثر قیمت نمی‌تواند منفی باشد."))
        return

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        print(farsi("حداقل قیمت نمی‌تواند بیشتر از حداکثر قیمت باشد."))
        return

    client = HttpClient()
    storage = DataStorage()

    normalized_brand = brand.strip() if brand else None

    if normalized_brand in BRAND_MAP:
        base_url = (
            "https://www.technolife.com/category/mobile/mobile-phone/"
            f"brand-{BRAND_MAP[normalized_brand]}"
        )
    else:
        base_url = (
            "https://www.technolife.com/category/mobile/mobile-phone"
        )

    all_products = []

    for page in range(1, total_pages + 1):
        page_url = (
            f"{base_url}?page={page}"
            if page > 1
            else base_url
        )

        print(farsi(f"در حال دریافت صفحه {page} از: {page_url}"))

        html_content = client.fetch_html(page_url)

        if not html_content:
            print(farsi(f"محتوای صفحه {page} دریافت نشد."))
            break

        products = ProductParser.parse_product_list(html_content)

        if not products:
            print(farsi(f"محصولی در صفحه {page} یافت نشد."))
            break

        all_products.extend(products)
        print(
            farsi(
                f"صفحه {page}: تعداد {len(products)} محصول استخراج شد."
            )
        )

    if not all_products:
        print(farsi("هیچ داده‌ای برای پردازش یافت نشد."))
        return

    # فیلتر برند در عنوان محصول
    if normalized_brand:
        print(
            farsi(
                f"\nدر حال بررسی و تطبیق نهایی برای برند: "
                f"{normalized_brand}"
            )
        )

        search_terms = [normalized_brand.lower()]

        if normalized_brand in BRAND_MAP:
            search_terms.append(BRAND_MAP[normalized_brand].lower())

        filtered_products = [
            product
            for product in all_products
            if any(
                term in product.get("title", "").lower()
                for term in search_terms
            )
        ]

        if filtered_products:
            all_products = filtered_products
            print(
                farsi(
                    f"تعداد محصولات پس از فیلتر برند: "
                    f"{len(all_products)}"
                )
            )
        else:
            print(farsi("محصولی با برند انتخاب‌شده در عنوان پیدا نشد."))

    # فیلتر بازه قیمت
    if min_price is not None or max_price is not None:
        filtered_products = []

        for product in all_products:
            price = product.get("price")

            if price is None:
                continue

            if min_price is not None and price < min_price:
                continue

            if max_price is not None and price > max_price:
                continue

            filtered_products.append(product)

        all_products = filtered_products

        print(
            farsi(
                f"تعداد محصولات پس از فیلتر قیمت: "
                f"{len(all_products)}"
            )
        )

    if not all_products:
        print(farsi("پس از اعمال فیلترها محصولی باقی نماند."))
        return

    # مرتب‌سازی بر اساس قیمت
    if sort_order:
        all_products.sort(
            key=lambda product: (
                product.get("price")
                if product.get("price") is not None
                else float("inf")
            ),
            reverse=sort_order == "desc",
        )

        sort_title = (
            "نزولی"
            if sort_order == "desc"
            else "صعودی"
        )

        print(farsi(f"مرتب‌سازی قیمت به‌صورت {sort_title} انجام شد."))

    base_filename = "technolife_mobiles"

    csv_path = None
    json_path = None
    excel_path = None

    if export_format in ("csv", "all"):
        csv_path = storage.save_to_csv(
            all_products,
            base_filename,
        )
        print(farsi(f"گزارش CSV: {csv_path}"))

    if export_format in ("json", "all"):
        json_path = storage.save_to_json(
            all_products,
            base_filename,
        )
        print(farsi(f"گزارش JSON: {json_path}"))

    if export_format in ("excel", "all"):
        excel_path = storage.save_to_excel(
            all_products,
            base_filename,
        )
        print(farsi(f"گزارش Excel: {excel_path}"))

    print(
        farsi(
            f"\nمجموع کل محصولات پردازش‌شده: "
            f"{len(all_products)}"
        )
    )
    print(farsi("عملیات استخراج و ذخیره‌سازی با موفقیت پایان یافت."))

    stats = analyze_products(
        all_products,
        brand=normalized_brand,
    )

    brand_title = (
        f" ({normalized_brand})"
        if normalized_brand
        else ""
    )

    print(farsi(f"\n--- آمار تحلیل محصولات{brand_title} ---"))
    print(farsi(f"تعداد کل: {stats['total']}"))

    min_p = (
        f"{stats['min_price']:,} تومان"
        if stats["min_price"] is not None
        else "نامشخص"
    )

    max_p = (
        f"{stats['max_price']:,} تومان"
        if stats["max_price"] is not None
        else "نامشخص"
    )

    avg_p = (
        f"{stats['avg_price']:,.0f} تومان"
        if stats["avg_price"] is not None
        else "نامشخص"
    )

    print(farsi(f"حداقل قیمت: {min_p}"))
    print(farsi(f"حداکثر قیمت: {max_p}"))
    print(farsi(f"میانگین قیمت: {avg_p}"))


def run_engine():
    """موتور مشاوره هوش مصنوعی اختیاری."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print(
            farsi(
                "خطا: کلید GROQ_API_KEY در فایل .env "
                "تعریف نشده است."
            )
        )
        return

    try:
        from scraper.ai import BookAIAssistant
    except ImportError:
        print(
            farsi(
                "ماژول scraper/ai.py یافت نشد. "
                "موتور AI در دسترس نیست."
            )
        )
        return

    ai_assistant = BookAIAssistant(api_key=GAPGPTMASKTOKEN78xf166cw4oX1X)

    print(
        farsi(
            "موتور هوش مصنوعی بارگذاری شد. "
            "(جهت خروج، exit را وارد کنید)"
        )
    )

    while True:
        user_query = input(farsi("پرسش شما: "))

        if user_query.strip().lower() in ["exit", "خروج"]:
            print(farsi("خروج از سامانه."))
            break

        response = ai_assistant.get_recommendation(user_query)
        print(farsi(f"پاسخ سیستم: {response}"))


def main():
    parser = argparse.ArgumentParser(
        description=farsi(
            "موتور رصد قیمت و استخراج محصولات"
        )
    )

    parser.add_argument(
        "--brand",
        type=str,
        default=None,
        help=farsi("فیلتر بر اساس نام برند"),
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help=farsi(
            "تعداد صفحات برای اسکرپ "
            "(پیش‌فرض: 1)"
        ),
    )

    parser.add_argument(
        "--chat",
        action="store_true",
        help=farsi(
            "اجرای موتور هوش مصنوعی به‌صورت تعاملی"
        ),
    )

    parser.add_argument(
        "--min-price",
        type=int,
        default=None,
        help=farsi("حداقل قیمت به تومان"),
    )

    parser.add_argument(
        "--max-price",
        type=int,
        default=None,
        help=farsi("حداکثر قیمت به تومان"),
    )

    parser.add_argument(
        "--sort",
        choices=["asc", "desc"],
        default=None,
        help=farsi(
            "مرتب‌سازی بر اساس قیمت: "
            "asc یا desc"
        ),
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "excel", "all"],
        default="all",
        help=farsi(
            "فرمت ذخیره‌سازی: "
            "csv، json، excel یا all"
        ),
    )

    args = parser.parse_args()

    if args.chat:
        run_engine()
        return

    run_scraper(
        total_pages=args.pages,
        brand=args.brand,
        min_price=args.min_price,
        max_price=args.max_price,
        sort_order=args.sort,
        export_format=args.format,
    )


if __name__ == "__main__":
    main()
