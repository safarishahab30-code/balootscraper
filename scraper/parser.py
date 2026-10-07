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
        """تبدیل متن قیمت به عدد صحیح با تبدیل اعداد فارسی و عربی"""
        if not raw_price or raw_price == "نامشخص":
            return 0

        # تبدیل اعداد فارسی و عربی به انگلیسی
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        english_digits = "0123456789"

        translation_table = str.maketrans(
            persian_digits + arabic_digits,
            english_digits + english_digits
        )
        normalized = raw_price.translate(translation_table)

        digits = re.sub(r"[^\d]", "", normalized)
        return int(digits) if digits else 0

    @classmethod
    def parse_product_list(cls, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        products = []
        seen_urls = set()

        # استخراج لینک‌های محصولات هر دو سایت (تکنولایف و زومیت)
        links = soup.find_all(
            "a",
            href=lambda h: h and (
                "/product-" in h or
                "/product/" in h or
                "zoomit.ir" in h
            )
        )

        for a_tag in links:
            raw_href = a_tag.get("href", "").strip()
            if not raw_href:
                continue

            # استانداردسازی و ساخت لینک کامل
            if raw_href.startswith("http"):
                full_url = raw_href
            else:
                full_url = urllib.parse.urljoin("https://www.technolife.com", raw_href)

            clean_url = full_url.split("?")[0]

            if clean_url in seen_urls:
                continue

            # ۱. استخراج عنوان محصول
            title = a_tag.get("title", "").strip()
            if not title:
                h_tag = a_tag.find(["h2", "h3", "h4", "p"])
                if h_tag and len(h_tag.get_text(strip=True)) > 5:
                    title = h_tag.get_text(strip=True)
                else:
                    text_inside = a_tag.get_text(separator=" ", strip=True)
                    if len(text_inside) > 5 and "تومان" not in text_inside:
                        title = text_inside

            # استخراج عنوان از اسلاگ در صورت نبود عنوان متنی
            if not title or len(title) < 5:
                path_part = urllib.parse.urlparse(clean_url).path
                slug = path_part.rstrip("/").split("/")[-1]
                decoded_slug = urllib.parse.unquote(slug).replace("-", " ").strip()
                if decoded_slug:
                    title = decoded_slug

            if not title:
                continue

            # ۲. استخراج قیمت: پیمایش المان‌های والد و استخراج عدد همراه با تومان
            price_text = "نامشخص"
            current_parent = a_tag

            for _ in range(5):
                current_parent = current_parent.parent
                if not current_parent:
                    break

                p_text = current_parent.get_text(separator=" ", strip=True)

                # تطبیق الگوهای: "۱۲,۰۰۰,۰۰۰ تومان" یا "از ۱۲,۰۰۰,۰۰۰ تومان" یا ریال
                price_match = re.search(
                    r"(?:از\s*)?([\d۰-۹٠-٩][\d۰-۹٠-٩,،\s]{2,20})\s*(?:تومان|تومن|ریال)",
                    p_text
                )

                if not price_match:
                    price_match = re.search(
                        r"(?:تومان|تومن|ریال)\s*([\d۰-۹٠-٩][\d۰-۹٠-٩,،\s]{2,20})",
                        p_text
                    )

                if price_match:
                    number_part = price_match.group(1).strip()
                    price_text = f"{number_part} تومان"
                    break

            price_int = cls.clean_price(price_text)

            # بررسی وضعیت موجودی
            parent_text = current_parent.get_text(separator=" ", strip=True) if current_parent else ""
            is_available = not any(
                phrase in parent_text
                for phrase in ("ناموجود", "اتمام موجودی", "موجود نیست")
            )

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
import requests

def fetch_zoomit_data():
    api_url = "PASTE_THE_COPIED_URL_HERE"
    headers = {"User-Agent": "Mozilla/5.0..."} # هدر ضروری است
    
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None
