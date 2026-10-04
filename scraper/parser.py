import sys
from pathlib import Path
from typing import List, Dict, Any

# تنظیم مسیر برای ایمپورت ماژول‌های داخلی
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scraper.utills import farsi

class DigikalaParser:
    """استخراج و تمیزسازی فیلدهای مورد نیاز از داده‌های خام API دیجی‌کالا"""
    
    @staticmethod
    def parse_product_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """استخراج اطلاعات ساختاریافته از یک محصول"""
        price_data = item.get("default_variant", {}).get("price", {})
        
        selling_price = price_data.get("selling_price", 0)
        rrp_price = price_data.get("rrp_price", 0)
        discount_percent = price_data.get("discount_percent", 0)
        
        # استخراج وضعیت موجودی
        is_available = item.get("status") == "marketable"
        
        return {
            "id": item.get("id"),
            "title_fa": item.get("title_fa", ""),
            "title_en": item.get("title_en", ""),
            "selling_price": selling_price,
            "rrp_price": rrp_price,
            "discount_percent": discount_percent,
            "is_available": is_available,
            "rating_rate": item.get("rating", {}).get("rate", 0),
            "rating_count": item.get("rating", {}).get("count", 0),
            "url": f"https://www.digikala.com{item.get('url', {}).get('uri', '')}"
        }

    @classmethod
    def parse_search_results(cls, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """پردازش تمام محصولات درون خروجی جستجو"""
        products = raw_data.get("data", {}).get("products", [])
        return [cls.parse_product_item(prod) for prod in products]


if __name__ == "__main__":
    from scraper.client import DigikalaClient
    
    print(farsi("در حال تست پارسر..."))
    client = DigikalaClient()
    raw = client.fetch_search_results(keyword="کتاب اثر مرکب", page=1)
    
    parsed = DigikalaParser.parse_search_results(raw)
    print(farsi(f"تعداد محصولات پارس‌شده: {len(parsed)}"))
    if parsed:
        first = parsed[0]
        print(farsi(f"عنوان: {first['title_fa']}"))
        print(farsi(f"قیمت فروش: {first['selling_price']} ریال"))
        print(farsi(f"موجودی: {first['is_available']}"))
