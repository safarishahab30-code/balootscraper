import sys
from pathlib import Path
import requests
from loguru import logger

# تنظیم مسیر برای ایمپورت ماژول‌های داخلی
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scraper.utils import farsi

class DigikalaClient:
    BASE_URL = "https://api.digikala.com/v1/search/"

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_search_results(self, keyword: str, page: int = 1) -> dict:
        params = {
            "q": keyword,
            "page": page
        }
        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(farsi(f"خطا در دریافت داده از دیجی‌کالا: {e}"))
            return {}

if __name__ == "__main__":
    print(farsi("شروع تست ارتباط با API دیجی‌کالا..."))
    client = DigikalaClient()
    res = client.fetch_search_results(keyword="کتاب اثر مرکب", page=1)
    
    # استخراج لیست محصولات از ساختار جدید دیجی‌کالا
    products = res.get("data", {}).get("products", [])
    print(farsi(f"تعداد محصولات یافت‌شده: {len(products)}"))
    
    if products:
        first = products[0]
        print(farsi(f"عنوان نمونه: {first.get('title_fa')}"))
        print(farsi(f"شناسه کالا: {first.get('id')}"))
