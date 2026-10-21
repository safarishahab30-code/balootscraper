# 🌰 اسکرپر بلوط (Baloot Scraper)

یک ابزار پایتونی ماژولار تمیز و قدرتمند برای استخراج پایش و تحلیل قیمت محصولات از فروشگاهها و پایگاههای نلاین ایرانی (**تکنولایف** و **زومیت**). این سامانه با رعایت اصول مهندسی نرمافزار الگوی طراحی Factory تستهای جامع خودکار و رابط کاربری تعاملی پایانه پیادهسازی شده است.

---

## ✨ ویژگیهای کلیدی

- **معماری ماژولار مبتنی بر Factory Pattern:** قابلیت گسترش و افزودن سریع فروشگاهها و خزندههای جدید بدون تغییر ساختار کلی.
- **رابط کاربری تعاملی پایانه (Interactive CLI):** مجهز به منوهای روان و پویا با کتابخانههای \questionary\ و \ich\ همراه با پشتیبانی کامل از چینش فارسی (RTL).
- **فیلترها و مرتبسازی پیشرفته:** امکان اعمال کف/سقف قیمت مرتبسازی صعودی و نزولی بر پایه قیمت واقعی و بیشترین درصد تخفیف.
- **ذخیرهسازی چندگانه (Multi-format Storage):** صدور خودکار گزارشها در قالب فایلهای \CSV\  \JSON\  \Excel (XLSX)\ و پایگاهداده رابطهای \SQLite\.
- **زمانبندی هوشمند خودکار (Scheduler):** اجرای تسکهای دورهای پایش نوسان قیمت در بازههای زمانی معین بدون نیاز به دخالت کاربر.
- **پوشش تستهای خودکار (Automated Testing):** مجهز به ۱۳ تست واحد و یکپارچه با \pytest\ برای تضمین پایداری پارسرها فیلترها و خط لوله ذخیرهسازی داده.

---

## 🏗 معماری و جریان پردازش داده (Data Flow)

\\\mermaid
flowchart TD
    A[وبسایت هدف: Technolife / Zoomit] -->|ارسال درخواست HTTP با مدیریت Timeout و Header| B[Scraper Client]
    B -->|پارس محتوا با BeautifulSoup4| C[Parser Factory]
    C -->|انطباق با قوانین اختصاصی سایت| D[تکنولایف / زومیت پارسر]
    D -->|تبدیل ارقام فارسی و نرمالسازی قیمت| E[Data Cleaner & Analyzer]
    E -->|اعمال شروط فیلتر و سورت| F[Export Pipeline]
    F --> G[(پایگاهداده SQLite)]
    F --> H[فایل Excel]
    F --> I[فایل CSV / JSON]
\\\

---

## 🛠 پشته فناوری (Tech Stack)

- **زبان برنامه نویسی:** Python 3.13
- **کلاینت شبکه و استخراج محتوا:** Requests, BeautifulSoup4
- **رابط کاربری و چیدمان فارسی:** Questionary, Rich, Arabic-Reshaper, Python-Bidi
- **پردازش و مدیریت داده:** Pandas, OpenPyXL
- **اجرای وظایف دورهای:** Schedule
- **موتور تست و تضمین کیفیت:** Pytest

---

## 📁 ساختار ماژولهای پروژه

\\\	ext
balootscraper/
├── scraper/
│   ├── client.py         # کلاینت ارسال درخواستهای HTTP و کنترل هدرها
│   ├── factory.py        # الگو فکتوری برای فراخوانی پویای پارسر مناسب
│   ├── parser.py         # پارسر صفحات و استخراج المانهای تکنولایف
│   ├── zoomit_parser.py  # پارسر مشخصات گارانتی و قیمتهای زومیت
│   ├── analyzer.py       # منطق اعمال فیلترها و سورت دادهها
│   ├── storage.py        # لایه ذخیرهسازی چندگانه دادهها
│   ├── scheduler.py      # مدیریت اجرای وظایف زمانبندیشده
│   └── utils.py          # توابع نرمالسازی کاراکترها و قیمتها
├── tests/
│   ├── test_filters.py   # اعتبارسنجی فیلتر و سورت قیمت و تخفیف
│   ├── test_parser.py    # تست استخراج و پاکسازی فرمت قیمتها
│   ├── test_scraper.py   # تست یکپارچگی انتخاب پارسر از فکتوری
│   └── test_storage.py   # تست صحت ایجاد و صدور فایلهای اکسل CSV و JSON
├── data/                 # دایرکتوری ذخیره فایلهای استخراجشده
├── auto_run.py           # اسکریپت اجرای وظایف زمانبندیشده
├── main.py               # نقطه شروع اجرای رابط کاربری تعاملی (CLI)
├── requirements.txt      # پیشنیازها و کتابخانههای مورد نیاز
└── README.md             # مستندات فنی و راهنمای کامل پروژه
\\\

---

## 🚀 راهنمای نصب و راهاندازی سریع

### ۱. فعالسازی محیط مجازی
\\\powershell
# در ویندوز (PowerShell)
.\venv\Scripts\Activate.ps1

# در لینوکس / مک
source venv/bin/activate
\\\

### ۲. نصب پکیجهای مورد نیاز
\\\ash
pip install -r requirements.txt
\\\

### ۳. اجرای رابط کاربری تعاملی (CLI)
\\\ash
python main.py
\\\

### ۴. اجرای مانیتورینگ خودکار دورهای
\\\ash
python auto_run.py
\\\

---

## 🧪 اجرای تستهای خودکار

تمامی بخشهای کلیدی سیستم اعم از فکتوری پارسرها فیلترها و لایه ذخیرهسازی دادهها دارای تستهای خودکار هستند. برای اجرای تستها:

\\\ash
pytest tests/ -v
\\\

نتیجه اجرای موفق تستها:
\\\	ext
tests/test_filters.py::test_filter_min_price PASSED               [  7%]
tests/test_filters.py::test_filter_max_price PASSED               [ 15%]
tests/test_filters.py::test_sort_price_desc PASSED                [ 23%]
tests/test_filters.py::test_sort_discount_desc PASSED             [ 30%]
tests/test_parser.py::test_clean_price PASSED                     [ 38%]
tests/test_parser.py::test_clean_price_empty PASSED               [ 46%]
tests/test_parser.py::test_parse_product_item_mock PASSED         [ 53%]
tests/test_scraper.py::test_get_parser_technolife PASSED          [ 61%]
tests/test_scraper.py::test_get_parser_zoomit PASSED              [ 69%]
tests/test_scraper.py::test_get_parser_invalid_domain PASSED      [ 76%]
tests/test_storage.py::test_save_to_json PASSED                    [ 84%]
tests/test_storage.py::test_save_to_csv PASSED                     [ 92%]
tests/test_storage.py::test_save_to_excel PASSED                   [100%]

============================= 13 passed in 0.77s =============================
\\\

---

## 📄 مجوز (License)

توسعه داده شده توسط **شهاب صفری** تحت مجوز MIT.
