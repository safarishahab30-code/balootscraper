import sys
from pathlib import Path
import requests
from loguru import logger

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
        """دریافت کد HTML خام صفحه بر اساس آدرس ورودی."""
        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(farsi(f"خطا در برقراری ارتباط با {url}: {e}"))
            return None


if __name__ == "__main__":
    print(farsi("شروع تست اتصال و دریافت HTML..."))
    client = HttpClient()
    test_url = "https://www.technolife.ir/product/list/69_70_79/%D8%AA%D9%85%D8%A7%D9%85%DB%8C-%DA%AF%D9%88%D8%B4%DB%8C%E2%80%8C%D9%87%D8%A7"
    html = client.fetch_html(test_url)

    if html:
        print(farsi(f"دریافت با موفقیت انجام شد. حجم داده: {len(html)} کاراکتر"))
    else:
        print(farsi("خطا در دریافت اطلاعات صفحه."))
