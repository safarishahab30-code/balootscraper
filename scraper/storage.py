import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# تنظیم مسیر برای ایمپورت ماژول‌های داخلی
sys.path.append(str(Path(__file__).resolve().parent.parent))
from scraper.utils import farsi

class DataStorage:
    """مدیریت ذخیره‌سازی داده‌ها در فرمت‌های مختلف"""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_to_excel(self, data: List[Dict[str, Any]], filename: str) -> str:
        """ذخیره داده‌ها در فرمت اکسل"""
        if not data:
            return ""
        filepath = self.output_dir / f"{filename}.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False, engine="openpyxl")
        return str(filepath)

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> Path:
        """ذخیره در قالب CSV با انکودینگ utf-8-sig برای سازگاری با اکسل"""
        filepath = self.output_dir / f"{filename}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        return filepath

    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> Path:
        """ذخیره در قالب JSON ساختاریافته"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def save_automated(self, data: List[Dict[str, Any]], prefix: str = "auto_job", file_type: str = "json") -> Path:
        """ذخیره اختصاصی برای تسک‌های اتوماسیون همراه با ثبت تاریخ و ساعت"""
        auto_dir = self.output_dir / "automation"
        auto_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}"
        
        # ذخیره بر اساس فرمت انتخابی
        if file_type == "csv":
            filepath = auto_dir / f"{filename}.csv"
            pd.DataFrame(data).to_csv(filepath, index=False, encoding="utf-8-sig")
        elif file_type == "excel":
            filepath = auto_dir / f"{filename}.xlsx"
            pd.DataFrame(data).to_excel(filepath, index=False, engine="openpyxl")
        else:
            filepath = auto_dir / f"{filename}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        return filepath

if __name__ == "__main__":
    from scraper.client import HttpClient
    from scraper.parser import ProductParser

    print(farsi("شروع تست ماژول ذخیره‌سازی..."))

    client = HttpClient()
    url = "https://www.technolife.com/category/mobile/mobile-phone/brand-samsung"
    html = client.fetch_html(url)

    if html:
        products = ProductParser.parse_product_list(html)
        print(farsi(f"تعداد رکوردهای آماده ذخیره: {len(products)}"))

        storage = DataStorage(output_dir="data")
        csv_path = storage.save_to_csv(products, "technolife_mobiles")
        json_path = storage.save_to_json(products, "technolife_mobiles")
        excel_path = storage.save_to_excel(products, "technolife_mobiles")

        print(farsi(f"فایل CSV ایجاد شد: {csv_path}"))
        print(farsi(f"فایل JSON ایجاد شد: {json_path}"))
        print(farsi(f"فایل اکسل ایجاد شد: {excel_path}"))
    else:
        print(farsi("خطا در دریافت اطلاعات برای تست ذخیره‌سازی."))
import sqlite3
from datetime import datetime

def save_to_db(products: list, db_path: str = "prices.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                link TEXT,
                scraped_at TEXT
            )
        """)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        records = [(p["title"], p["price"], p["link"], now) for p in products]
        cursor.executemany(
            "INSERT INTO price_history (title, price, link, scraped_at) VALUES (?, ?, ?, ?)",
            records
        )
        conn.commit()
from datetime import datetime, timedelta

def init_tracker_table(conn):
    """ایجاد جدول پیگیری لینک‌ها و دوره‌های اسکرپ"""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tracked_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                interval_days INTEGER DEFAULT 3,
                last_scraped_at TIMESTAMP
            )
        """)

def should_scrape(conn, url: str, interval_days: int = 3) -> bool:
    """بررسی اینکه آیا ۳ روز گذشته و نیاز به اسکرپ دارد یا خیر"""
    cursor = conn.cursor()
    cursor.execute("SELECT last_scraped_at FROM tracked_targets WHERE url = ?", (url,))
    row = cursor.fetchone()
    
    if not row or not row[0]:
        return True  # بار اول است
    
    last_date = datetime.fromisoformat(row[0])
    return datetime.now() >= last_date + timedelta(days=interval_days)

def update_tracker(conn, url: str, interval_days: int = 3):
    """به‌روزرسانی تاریخ آخرین اسکرپ برای لینک"""
    with conn:
        conn.execute("""
            INSERT INTO tracked_targets (url, interval_days, last_scraped_at)
            VALUES (?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                last_scraped_at = excluded.last_scraped_at,
                interval_days = excluded.interval_days
        """, (url, interval_days, datetime.now().isoformat()))
