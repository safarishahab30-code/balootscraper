# 🌰 اسکرپر بلوط (Baloot Scraper)

یک ابزار پایتونی ماژولار و قدرتمند برای استخراج و پایش قیمت محصولات از فروشگاه‌های آنلاین ایرانی (تکنولایف و زومیت). این پروژه با رعایت اصول مهندسی نرم‌افزار برای مقیاس‌پذیری و نگهداری آسان طراحی شده است.

---

## ✨ ویژگی‌های کلیدی
- **معماری چندمنبعی:** پیاده‌سازی شده با الگوی طراحی Factory برای افزودن آسان فروشگاه‌های جدید.
- **رابط کاربری تعاملی (CLI):** مجهز به منوهای تعاملی با کتابخانه `questionary` و پشتیبانی کامل از زبان فارسی (RTL).
- **زمان‌بندی خودکار:** قابلیت اجرای تسک‌های پایش قیمت در بازه‌های زمانی مشخص.
- **ذخیره‌سازی چندگانه:** خروجی‌گیری داده‌ها در فرمت‌های `CSV` ، `JSON` و `Excel`.

---

## 🛠 تکنولوژی‌های مورد استفاده
- **زبان:** Python 3.10+
- **وب و پارسینگ:** `requests`, `BeautifulSoup4`
- **رابط کاربری:** `questionary`, `rich`, `arabic-reshaper`, `python-bidi`
- **مدیریت داده:** `pandas`, `openpyxl`

---

## 🚀 راهنمای شروع سریع

### ۱. دریافت پروژه و آماده‌سازی محیط
```bash
git clone https://github.com/safarishahab30-code/balootscraper.git
cd balootscraper
python -m venv venv
# در ویندوز:
venv\Scripts\activate
# در لینوکس/مک:
source venv/bin/activate
pip install -r requirements.txt
2. Run Interactive CLI
bash
python main.py
3. Run Automated Scheduler
bash
python auto_run.py
text

---

### گام دوم: مدیریت پیشرفته خطا و Retry (در `scraper/client.py`)
برای جلوگیری از کرش هنگام قطعی لحظه‌ای اینترنت، منطق Retry استاندارد را اضافه کن. تکه‌کد زیر را درون متد درخواست HTTP کلاس خود قرار بده:

```python
import time
import requests

def get_page(self, url, retries=3, backoff=2):
    for attempt in range(1, retries + 1):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt == retries:
                raise e
            time.sleep(backoff * attempt)



----------------------------------------------------------------------------------
# 🌰 Baloot Scraper

A robust, modular Python web scraper designed to extract and monitor product data and pricing from Iranian e-commerce platforms (Technolife & Zoomit).

---

## ✨ Features
- **Multi-source Architecture:** Built using the Factory Pattern for scalable scrapers.
- **Interactive CLI:** Terminal UI powered by `questionary` with full RTL/Persian support.
- **Automated Task Scheduling:** Periodic scraping and monitoring routines.
- **Multi-format Storage:** Exporting to `CSV`, `JSON`, and `Excel`.

---

## 🛠 Tech Stack
- **Language:** Python 3.10+
- **HTTP & Parsing:** `requests`, `BeautifulSoup4`
- **CLI & Formatting:** `questionary`, `rich`, `arabic-reshaper`, `python-bidi`
- **Data Export:** `pandas`, `openpyxl`

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/safarishahab30-code/balootscraper.git
cd balootscraper
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
