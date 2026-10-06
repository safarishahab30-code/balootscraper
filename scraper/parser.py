import re
import sys
import urllib.parse
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# تنظیم مسیر برای ایمپورت ماژول‌های داخلی
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scraper.utils import farsi


class ProductParser:
    """استخراج و ساختاردهی اطلاعات محصولات از کدهای HTML خام"""

    @classmethod
    def clean_price(cls, raw_price: str) -> int:
        """تبدیل متن قیمت به عدد صحیح"""
        if not raw_price or raw_price == "نامشخص":
            return 0

        # تبدیل اعداد فارسی/عربی به انگلیسی در صورت وجود
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"
        translation_table = str.maketrans(persian_digits, english_digits)
        normalized = raw_price.translate(translation_table)

        digits = re.sub(r"[^\d]", "", normalized)
        return int(digits) if digits else 0

    @classmethod
    def parse_product_list(cls, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        products = []
        seen_urls = set()

        links = soup.find_all("a", href=lambda h: h and "/product-" in h)

        for a_tag in links:
            raw_href = a_tag.get("href", "").strip()
            if not raw_href:
                continue

            full_url = raw_href if raw_href.startswith("http") else f"https://www.technolife.com{raw_href}"
            clean_url = full_url.split("?")[0]

            if clean_url in seen_urls:
                continue

            # ۱. استخراج عنوان اختصاصی هر محصول
            title = a_tag.get("title", "").strip()
            if not title:
                h_tag = a_tag.find(["h2", "h3", "h4", "p"])
                if h_tag and len(h_tag.get_text(strip=True)) > 5:
                    title = h_tag.get_text(strip=True)
                else:
                    text_inside = a_tag.get_text(separator=" ", strip=True)
                    if len(text_inside) > 5 and "تومان" not in text_inside:
                        title = text_inside

            # استخراج عنوان از اسلاگ URL در صورت پیدا نشدن
            if not title or len(title) < 5:
                path_part = clean_url.split("/product-")[-1]
                slug = path_part.split("/", 1)[-1] if "/" in path_part else ""
                decoded_slug = urllib.parse.unquote(slug).replace("-", " ").strip()
                if decoded_slug:
                    title = decoded_slug

            if not title:
                continue

            # ۲. استخراج قیمت: جستجوی والد نزدیک و استخراج عدد همراه با تومان
            price_text = "نامشخص"
            current_parent = a_tag
            for _ in range(5):
                current_parent = current_parent.parent
                if not current_parent:
                    break
                p_text = current_parent.get_text(separator=" ", strip=True)
                if "تومان" in p_text:
                    match = re.search(r"([\d\u06F0-\u06F9,،]{3,15})\s*تومان|تومان\s*([\d\u06F0-\u06F9,،]{3,15})", p_text)
                    if match:
                        num_part = match.group(1) or match.group(2)
                        price_text = f"{num_part} تومان"
                        break

            price_int = cls.clean_price(price_text)
            is_available = "ناموجود" not in (current_parent.get_text() if current_parent else "")

            products.append({
                "title": title,
                "price_raw": price_text,
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

    url = "https://www.technolife.com/category/mobile/mobile-phone/brand-samsung"
    html = client.fetch_html(url)

    if html:
        items = ProductParser.parse_product_list(html)
        print(farsi(f"تعداد محصولات استخراج‌شده: {len(items)}"))

        if items:
            sample = items[0]
            print(farsi(f"عنوان: {sample['title']}"))
            print(farsi(f"قیمت خام: {sample['price_raw']}"))
            print(farsi(f"قیمت عددی: {sample['price']}"))
            print(farsi(f"موجودی: {sample['available']}"))
            print(farsi(f"لینک: {sample['url']}"))
    else:
        print(farsi("خطا: صفحه‌ای دریافت نشد."))
