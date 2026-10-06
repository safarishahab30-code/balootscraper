import time
import schedule
from pathlib import Path
import sys

# تنظیم مسیر برای ایمپورت ماژول‌های داخلی
sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraper.utils import farsi
from scraper.client import HttpClient
from scraper.parser import ProductParser
from scraper.storage import DataStorage

class ScraperScheduler:
    """مدیریت زمان‌بندی اجرای خودکار اسکرپر تکنولایف"""

    def __init__(self, interval_minutes: int = 60):
        self.interval_minutes = interval_minutes
        self.client = HttpClient()
        self.storage = DataStorage()
        self.target_url = "https://www.technolife.com/category/mobile/mobile-phone/brand-samsung"

    def job(self):
        """وظیفه‌ای که در هر بازه زمانی اجرا می‌شود"""
        print(farsi(f"شروع اجرای خودکار تسک اسکرپ در ساعت: {time.strftime('%Y-%m-%d %H:%M:%S')}"))
        
        html = self.client.fetch_html(self.target_url)
        if html:
            products = ProductParser.parse_product_list(html)
            if products:
                # ذخیره خودکار با متد اختصاصی اتوماسیون
                saved_path = self.storage.save_automated(products, prefix="technolife_auto", file_type="json")
                print(farsi(f"اطلاعات با موفقیت ذخیره شد در مسیر: {saved_path}"))
            else:
                print(farsi("داده‌ای از صفحه استخراج نشد."))
        else:
            print(farsi("خطا در دریافت اطلاعات از وب‌سایت."))

    def start(self):
        """راه‌اندازی موتور زمان‌بندی"""
        print(farsi(f"هر {self.interval_minutes} دقیقه یک‌بار تسک اجرا خواهد شد..."))        
        # تنظیم زمان‌بندی (مثلاً هر X دقیقه یا ساعت مشخص)
        schedule.every(self.interval_minutes).minutes.do(self.job)

        # اجرای اولیه برای تست در لحظه شروع (اختیاری)
        # self.job()

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    # تست اجرای زمان‌بند (هر 1 ساعت یا برای تست سریع‌تر، تغییر به دقیقه دلخواه)
    scheduler = ScraperScheduler(interval_minutes=60)
    scheduler.start()
