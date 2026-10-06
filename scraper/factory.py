from scraper.parser import ProductParser
from scraper.zoomit_parser import ZoomitParser

def get_parser(url: str):
    """تشخیص خودکار پارسر بر اساس دامنه لینک"""
    if "technolife.ir" in url:
        return ProductParser()
    elif "zoomit.ir" in url:
        return ZoomitParser()
    else:
        raise ValueError("دامنه وارد شده پشتیبانی نمی‌شود. فقط تکنولایف و زومیت مجاز است.")
