import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

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


if __name__ == "__main__":
    from scraper.client import HttpClient
    from scraper.parser import ProductParser

    print(farsi("شروع تست ماژول ذخیره‌سازی..."))

    client = HttpClient()
    url = "https://www.technolife.ir/product/list/69_70_79/تمامی-گوشی%E2%80%8Cها"
    html = client.fetch_html(url)

    if html:
        products = ProductParser.parse_product_list(html)
        print(farsi(f"تعداد رکوردهای آماده ذخیره: {len(products)}"))

        storage = DataStorage(output_dir="data")
        csv_path = storage.save_to_csv(products, "technolife_mobiles")
        json_path = storage.save_to_json(products, "technolife_mobiles")

        print(farsi(f"فایل CSV ایجاد شد: {csv_path}"))
        print(farsi(f"فایل JSON ایجاد شد: {json_path}"))
    else:
        print(farsi("خطا در دریافت اطلاعات برای تست ذخیره‌سازی."))
