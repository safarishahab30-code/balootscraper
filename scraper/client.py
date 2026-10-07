import sys
from pathlib import Path
import requests
from loguru import logger

# تنظیم مسیر برای دسترسی به ماژول‌های پروژه
sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraper.utils import farsi

class HttpClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fa,en;q=0.9",
        }

    def fetch_html(self, url: str) -> str | None:
        """دریافت کد HTML خام صفحه با مدیریت دامنه ir."""
        # اصلاح دامنه قبل از درخواست برای جلوگیری از ریدایرکت ناخواسته
        url = url.replace(".com", ".ir")

        try:
            # غیرفعال کردن ریدایرکت خودکار جهت کنترل دقیق روی دامین ir
            response = requests.get(url, headers=self.headers, timeout=12, allow_redirects=False)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(farsi(f"خطا در برقراری ارتباط با {url}: {e}"))
            return None

if __name__ == "__main__":
    client = HttpClient()
    # تست با دامین صحیح و فرمت استاندارد تکنولایف
    test_url = "https://www.technolife.ir/product/list/164_163_130"
    print(farsi("شروع تست اتصال و دریافت HTML..."))
    html = client.fetch_html(test_url)

    if html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        page_title = soup.title.string.strip() if soup.title else "بدون عنوان"
        print(farsi(f"عنوان صفحه دریافت شده: {page_title}"))
        print(farsi(f"حجم داده: {len(html)} کاراکتر"))
    else:
        print(farsi("خطا در دریافت اطلاعات صفحه."))
