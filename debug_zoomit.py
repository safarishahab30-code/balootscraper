import requests
from scraper.utils import farsi

def dump_zoomit_mobile():
    url = "https://www.zoomit.ir/product/list/mobile/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(farsi("در حال دریافت لیست محصولات موبایل زومیت..."))
        response = requests.get(url, headers=headers, timeout=12)
        
        with open("zoomit_mobile_dump.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        print(farsi("فایل zoomit_mobile_dump.html ساخته شد."))
    except Exception as e:
        print(farsi(f"خطا در دریافت: {e}"))

if __name__ == "__main__":
    dump_zoomit_mobile()
