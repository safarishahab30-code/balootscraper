import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


# تنظیم مسیر برای ایمپورت ماژول‌های داخلی پروژه
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scraper.utils import farsi


class ProductParser:
    """استخراج و ساختاردهی اطلاعات محصولات از HTML خام."""

    # ارقام فارسی، عربی و انگلیسی
    DIGITS_PATTERN = r"\d۰-۹٠-٩"

    # واحدهای قابل پشتیبانی
    CURRENCY_PATTERN = r"تومان|تومن|ریال"

    # الگوی دقیق قیمت:
    # 69,300,000
    # ۶۹,۳۰۰,۰۰۰
    # 69 300 000
    # 69300000
    PRICE_PATTERN = re.compile(
        rf"""
        (?<![{DIGITS_PATTERN}])
        (
            [{DIGITS_PATTERN}]{{1,3}}
            (?:\s*[,،]\s*[{DIGITS_PATTERN}]{{3}})+

            |

            [{DIGITS_PATTERN}]{{1,3}}
            (?:\s+[{DIGITS_PATTERN}]{{3}}){{1,4}}

            |

            [{DIGITS_PATTERN}]{{5,}}
        )
        \s*
        ({CURRENCY_PATTERN})
        """,
        re.VERBOSE
    )

    @classmethod
    def normalize_digits(cls, text: str) -> str:
        """تبدیل اعداد فارسی و عربی به اعداد انگلیسی."""
        if not text:
            return ""

        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        english_digits = "0123456789"

        translation_table = str.maketrans(
            persian_digits + arabic_digits,
            english_digits + english_digits
        )

        return text.translate(translation_table)

    @classmethod
    def clean_price(cls, raw_price: str) -> int:
        """
        تبدیل متن قیمت به عدد صحیح.

        خروجی قیمت برحسب تومان است.
        اگر قیمت با واحد ریال باشد، به تومان تبدیل می‌شود.
        """
        if not raw_price or raw_price == "نامشخص":
            return 0

        normalized = cls.normalize_digits(raw_price)

        # جست‌وجوی قیمت دقیق قبل از واحد پول
        matches = list(cls.PRICE_PATTERN.finditer(normalized))

        if matches:
            # معمولاً آخرین قیمت داخل کارت، قیمت نهایی فروش است
            selected_match = matches[-1]

            number_part = selected_match.group(1)
            currency = selected_match.group(2)

            clean_digits = re.sub(r"[^\d]", "", number_part)

            if not clean_digits:
                return 0

            price = int(clean_digits)

            # تبدیل ریال به تومان
            if currency == "ریال":
                price //= 10

            return price

        # حالت جایگزین برای ورودی‌هایی که واحد پول ندارند
        number_matches = re.findall(
            r"\d{1,3}(?:[,،]\d{3})+|\d{5,}",
            normalized
        )

        if not number_matches:
            return 0

        # آخرین عدد معتبر انتخاب می‌شود
        clean_digits = re.sub(r"[^\d]", "", number_matches[-1])

        return int(clean_digits) if clean_digits else 0

    @classmethod
    def extract_price_from_text(
        cls,
        text: str
    ) -> Optional[Tuple[str, int]]:
        """
        استخراج قیمت معتبر از متن کامل کارت محصول.

        خروجی:
            (متن قیمت، قیمت عددی برحسب تومان)
        """
        if not text:
            return None

        normalized = cls.normalize_digits(text)
        matches = list(cls.PRICE_PATTERN.finditer(normalized))

        if not matches:
            return None

        # آخرین قیمت معمولاً قیمت نهایی پس از تخفیف است
        selected_match = matches[-1]

        number_part = selected_match.group(1)
        currency = selected_match.group(2)

        # حذف فاصله‌های اطراف کاما
        normalized_number = re.sub(r"\s*[,،]\s*", ",", number_part)

        # حذف فاصله در قیمت‌هایی مثل 69 300 000
        normalized_number = normalized_number.replace(" ", "")

        price_raw = f"{normalized_number} {currency}"
        price_int = cls.clean_price(price_raw)

        return price_raw, price_int

    @classmethod
    def extract_title(
        cls,
        a_tag,
        clean_url: str
    ) -> str:
        """استخراج عنوان محصول از تگ، متن کارت یا اسلاگ لینک."""

        # روش اول: ویژگی title
        title = a_tag.get("title", "").strip()

        if title and len(title) >= 5:
            return title

        # روش دوم: تگ‌های عنوان داخل لینک
        heading_tag = a_tag.find(["h1", "h2", "h3", "h4"])

        if heading_tag:
            heading_text = heading_tag.get_text(
                separator=" ",
                strip=True
            )

            if len(heading_text) >= 5:
                return heading_text

        # روش سوم: پاراگراف داخل لینک
        paragraph_tag = a_tag.find("p")

        if paragraph_tag:
            paragraph_text = paragraph_tag.get_text(
                separator=" ",
                strip=True
            )

            if (
                len(paragraph_text) >= 5
                and "تومان" not in paragraph_text
                and "ریال" not in paragraph_text
            ):
                return paragraph_text

        # روش چهارم: متن کامل داخل لینک
        text_inside = a_tag.get_text(separator=" ", strip=True)

        if (
            len(text_inside) >= 5
            and "تومان" not in text_inside
            and "تومن" not in text_inside
            and "ریال" not in text_inside
        ):
            return text_inside

        # روش پنجم: استخراج عنوان از اسلاگ URL
        path_part = urllib.parse.urlparse(clean_url).path
        slug = path_part.rstrip("/").split("/")[-1]

        decoded_slug = urllib.parse.unquote(slug)
        decoded_slug = decoded_slug.replace("-", " ").strip()

        # حذف شناسه احتمالی ابتدای آدرس تکنولایف
        decoded_slug = re.sub(
            r"^product\s*\d*\s*",
            "",
            decoded_slug,
            flags=re.IGNORECASE
        ).strip()

        return decoded_slug

    @classmethod
    def build_full_url(
        cls,
        raw_href: str,
        base_url: str
    ) -> str:
        """تبدیل لینک نسبی محصول به لینک کامل."""

        if raw_href.startswith(("http://", "https://")):
            full_url = raw_href
        else:
            full_url = urllib.parse.urljoin(base_url, raw_href)

        # حذف پارامترهای تبلیغاتی و کوئری‌های اضافی
        parsed_url = urllib.parse.urlsplit(full_url)

        return urllib.parse.urlunsplit((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            "",
            ""
        ))

    @classmethod
    def parse_product_list(
        cls,
        html_content: str,
        base_url: str = "https://www.technolife.com"
    ) -> List[Dict[str, Any]]:
        """استخراج فهرست محصولات از HTML تکنولایف یا سایت مشابه."""

        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")

        products: List[Dict[str, Any]] = []
        seen_urls = set()

        links = soup.find_all(
            "a",
            href=lambda href: href and (
                "/product-" in href
                or "/product/" in href
                or "technolife.com/product" in href
                or "zoomit.ir/product" in href
            )
        )

        for a_tag in links:
            raw_href = a_tag.get("href", "").strip()

            if not raw_href:
                continue

            clean_url = cls.build_full_url(
                raw_href=raw_href,
                base_url=base_url
            )

            if clean_url in seen_urls:
                continue

            title = cls.extract_title(
                a_tag=a_tag,
                clean_url=clean_url
            )

            if not title or len(title) < 5:
                continue

            price_raw = "نامشخص"
            price_int = 0
            product_text = ""

            current_parent = a_tag

            # حرکت در والدهای لینک برای رسیدن به کارت کامل محصول
            for _ in range(6):
                current_parent = current_parent.parent

                if current_parent is None:
                    break

                parent_text = current_parent.get_text(
                    separator=" ",
                    strip=True
                )

                # جلوگیری از بررسی والدهای بسیار بزرگ مثل body
                if len(parent_text) > 5000:
                    break

                product_text = parent_text

                extracted_price = cls.extract_price_from_text(parent_text)

                if extracted_price:
                    price_raw, price_int = extracted_price
                    break

            # اگر متن مناسبی از والد پیدا نشد، متن خود لینک بررسی شود
            if not product_text:
                product_text = a_tag.get_text(
                    separator=" ",
                    strip=True
                )

            unavailable_phrases = (
                "ناموجود",
                "اتمام موجودی",
                "موجود نیست",
                "در حال حاضر موجود نیست",
                "به‌زودی"
            )

            is_available = not any(
                phrase in product_text
                for phrase in unavailable_phrases
            )

            products.append({
                "title": title,
                "price_raw": price_raw,
                "price": price_int,
                "available": is_available,
                "url": clean_url
            })

            seen_urls.add(clean_url)

        return products


if __name__ == "__main__":
    from scraper.client import HttpClient

    print(farsi("در حال تست پارسر HTML..."))

    client = HttpClient()

    url = (
        "https://www.technolife.com/"
        "category/mobile/mobile-phone/brand-samsung"
    )

    html = client.fetch_html(url)

    if not html:
        print(farsi("خطا: صفحه‌ای دریافت نشد."))
        sys.exit(1)

    items = ProductParser.parse_product_list(
        html_content=html,
        base_url="https://www.technolife.com"
    )

    print(farsi(f"تعداد محصولات استخراج‌شده: {len(items)}"))

    if not items:
        print(farsi("هیچ محصولی استخراج نشد."))
        sys.exit(0)

    sample = items[0]

    print(farsi("-" * 40))
    print(farsi(f"عنوان: {sample['title']}"))
    print(farsi(f"قیمت خام: {sample['price_raw']}"))
    print(farsi(f"قیمت عددی: {sample['price']:,} تومان"))
    print(farsi(f"موجودی: {sample['available']}"))
    print(farsi(f"لینک: {sample['url']}"))
