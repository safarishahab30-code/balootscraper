import argparse
import sys
from datetime import datetime
from pathlib import Path

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scraper.analyzer import analyze_products
from scraper.client import HttpClient
from scraper.parser import ProductParser
from scraper.storage import DataStorage
from scraper.utils import farsi


console = Console()
DATA_DIR = Path("data")
CANCELLED = object()


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
    """استخراج، فیلتر، مرتب‌سازی و ذخیره محصولات موبایل."""

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
                f"صفحه {page}: تعداد {len(products)} "
                "محصول استخراج شد."
            )
        )

    if not all_products:
        print(farsi("هیچ داده‌ای برای پردازش یافت نشد."))
        return

    # فیلتر نهایی برند بر اساس عنوان محصول
    if normalized_brand:
        print(
            farsi(
                "\nدر حال بررسی و تطبیق نهایی برای برند: "
                f"{normalized_brand}"
            )
        )

        search_terms = [normalized_brand.lower()]

        if normalized_brand in BRAND_MAP:
            search_terms.append(BRAND_MAP[normalized_brand].lower())

        all_products = [
            product
            for product in all_products
            if any(
                term in product.get("title", "").lower()
                for term in search_terms
            )
        ]

        print(
            farsi(
                "تعداد محصولات پس از فیلتر برند: "
                f"{len(all_products)}"
            )
        )

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
                "تعداد محصولات پس از فیلتر قیمت: "
                f"{len(all_products)}"
            )
        )

    if not all_products:
        print(farsi("پس از اعمال فیلترها محصولی باقی نماند."))
        return

    # مرتب‌سازی بر اساس قیمت
    if sort_order:
        products_with_price = [
            product
            for product in all_products
            if product.get("price") is not None
        ]

        products_without_price = [
            product
            for product in all_products
            if product.get("price") is None
        ]

        products_with_price.sort(
            key=lambda product: product["price"],
            reverse=sort_order == "desc",
        )

        all_products = products_with_price + products_without_price

        sort_title = (
            "نزولی"
            if sort_order == "desc"
            else "صعودی"
        )

        print(
            farsi(
                f"مرتب‌سازی قیمت به‌صورت {sort_title} انجام شد."
            )
        )

    base_filename = "technolife_mobiles"

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
            "\nمجموع کل محصولات پردازش‌شده: "
            f"{len(all_products)}"
        )
    )

    print(
        farsi(
            "عملیات استخراج و ذخیره‌سازی با موفقیت پایان یافت."
        )
    )

    stats = analyze_products(
        all_products,
        brand=normalized_brand,
    )

    brand_title = (
        f" ({normalized_brand})"
        if normalized_brand
        else ""
    )

    print(
        farsi(
            f"\n--- آمار تحلیل محصولات{brand_title} ---"
        )
    )

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


def normalize_digits(value: str) -> str:
    """تبدیل ارقام فارسی و عربی به ارقام انگلیسی."""

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"

    translation_table = str.maketrans(
        persian_digits + arabic_digits,
        english_digits + english_digits,
    )

    return value.translate(translation_table)


def ask_integer(
    prompt: str,
    default: int = None,
    minimum: int = 0,
    allow_empty: bool = False,
):
    """دریافت عدد از کاربر."""

    default_value = (
        ""
        if default is None
        else str(default)
    )

    while True:
        answer = questionary.text(
            farsi(prompt),
            default=default_value,
        ).ask()

        if answer is None:
            return CANCELLED

        normalized_answer = normalize_digits(
            answer.strip()
        )

        normalized_answer = (
            normalized_answer
            .replace(",", "")
            .replace("٬", "")
            .replace("،", "")
        )

        if not normalized_answer and allow_empty:
            return None

        try:
            number = int(normalized_answer)
        except ValueError:
            print(farsi("لطفاً یک عدد معتبر وارد کن."))
            continue

        if number < minimum:
            print(
                farsi(
                    f"عدد واردشده باید حداقل {minimum} باشد."
                )
            )
            continue

        return number


def show_saved_files():
    """نمایش فایل‌های خروجی اسکرپر."""

    valid_extensions = {
        ".csv",
        ".json",
        ".xlsx",
    }

    if not DATA_DIR.exists():
        print(
            farsi(
                "پوشه data هنوز ساخته نشده و خروجی‌ای وجود ندارد."
            )
        )
        return

    files = [
        path
        for path in DATA_DIR.glob("technolife_mobiles.*")
        if (
            path.is_file()
            and path.suffix.lower() in valid_extensions
        )
    ]

    if not files:
        print(
            farsi(
                "هنوز فایل خروجی‌ای در پوشه data پیدا نشد."
            )
        )
        return

    files.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    table = Table(
        title=farsi("فایل‌های خروجی"),
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column(farsi("نام فایل"))
    table.add_column(farsi("فرمت"))
    table.add_column(farsi("آخرین تغییر"))

    for file_path in files:
        modified_time = datetime.fromtimestamp(
            file_path.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M")

        table.add_row(
            farsi(file_path.name),
            file_path.suffix.upper().lstrip("."),
            modified_time,
        )

    console.print(table)


def run_custom_scrape():
    """گرفتن تنظیمات از کاربر و اجرای اسکرپر."""

    brand_choices = [
        Choice(
            farsi("همه برندها"),
            value="all",
        )
    ]

    brand_choices.extend(
        Choice(
            farsi(brand_name),
            value=brand_name,
        )
        for brand_name in BRAND_MAP
    )

    selected_brand = questionary.select(
        farsi("برند مورد نظر را انتخاب کن:"),
        choices=brand_choices,
    ).ask()

    if selected_brand is None:
        return

    brand = (
        None
        if selected_brand == "all"
        else selected_brand
    )

    pages = ask_integer(
        "تعداد صفحات برای استخراج:",
        default=1,
        minimum=1,
    )

    if pages is CANCELLED:
        return

    min_price = ask_integer(
        "حداقل قیمت به تومان؛ برای نداشتن حداقل، خالی بگذار:",
        minimum=0,
        allow_empty=True,
    )

    if min_price is CANCELLED:
        return

    max_price = ask_integer(
        "حداکثر قیمت به تومان؛ برای نداشتن حداکثر، خالی بگذار:",
        minimum=0,
        allow_empty=True,
    )

    if max_price is CANCELLED:
        return

    sort_choice = questionary.select(
        farsi("مرتب‌سازی قیمت را انتخاب کن:"),
        choices=[
            Choice(
                farsi("بدون مرتب‌سازی"),
                value="none",
            ),
            Choice(
                farsi("صعودی؛ ارزان‌ترین ابتدا"),
                value="asc",
            ),
            Choice(
                farsi("نزولی؛ گران‌ترین ابتدا"),
                value="desc",
            ),
        ],
    ).ask()

    if sort_choice is None:
        return

    format_choice = questionary.select(
        farsi("فرمت ذخیره‌سازی را انتخاب کن:"),
        choices=[
            Choice("CSV", value="csv"),
            Choice("JSON", value="json"),
            Choice("Excel", value="excel"),
            Choice(
                farsi("همه فرمت‌ها"),
                value="all",
            ),
        ],
    ).ask()

    if format_choice is None:
        return

    run_scraper(
        total_pages=pages,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        sort_order=(
            None
            if sort_choice == "none"
            else sort_choice
        ),
        export_format=format_choice,
    )


def run_interactive_menu():
    """نمایش منوی اصلی تعاملی."""

    console.print(
        Panel.fit(
            Text(
                farsi(
                    "سیستم استخراج و پایش قیمت تکنولایف"
                )
            ),
            border_style="cyan",
        )
    )

    menu_choices = [
        Choice(
            farsi(
                "شروع استخراج سریع با تنظیمات پیش‌فرض"
            ),
            value="quick",
        ),
        Choice(
            farsi(
                "استخراج با فیلتر و تنظیمات سفارشی"
            ),
            value="custom",
        ),
        Choice(
            farsi(
                "نمایش فایل‌های خروجی ذخیره‌شده"
            ),
            value="files",
        ),
        Choice(
            farsi("خروج"),
            value="exit",
        ),
    ]

    while True:
        try:
            action = questionary.select(
                farsi("عملیات مورد نظر را انتخاب کن:"),
                choices=menu_choices,
            ).ask()

        except (KeyboardInterrupt, EOFError):
            print(farsi("\nخروج از منو."))
            return

        if action is None or action == "exit":
            print(farsi("خروج از برنامه."))
            return

        if action == "quick":
            run_scraper()

        elif action == "custom":
            run_custom_scrape()

        elif action == "files":
            show_saved_files()


def build_argument_parser():
    """ساخت پارسر آرگومان‌های خط فرمان."""

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
            "تعداد صفحات برای اسکرپ؛ پیش‌فرض: ۱"
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
            "مرتب‌سازی قیمت: asc یا desc"
        ),
    )

    parser.add_argument(
        "--format",
        choices=[
            "csv",
            "json",
            "excel",
            "all",
        ],
        default="all",
        help=farsi(
            "فرمت ذخیره‌سازی: csv، json، excel یا all"
        ),
    )

    return parser


def main():
    parser = build_argument_parser()
    args = parser.parse_args()

    try:
        # اجرای بدون آرگومان، منوی تعاملی را باز می‌کند.
        if len(sys.argv) == 1:
            run_interactive_menu()
            return

        run_scraper(
            total_pages=args.pages,
            brand=args.brand,
            min_price=args.min_price,
            max_price=args.max_price,
            sort_order=args.sort,
            export_format=args.format,
        )

    except KeyboardInterrupt:
        print(farsi("\nعملیات توسط کاربر متوقف شد."))


if __name__ == "__main__":
    main()
