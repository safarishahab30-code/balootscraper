import pytest
from scraper.parser import ProductParser


def test_clean_price():
    """تست پاک‌سازی و تبدیل رشته قیمت فارسی به عدد صحیح"""
    raw_price = "۴۴,۹۹۹,۰۰۰ تومان"
    cleaned = ProductParser.clean_price(raw_price)
    assert cleaned == 44999000


def test_clean_price_empty():
    """تست خروجی قیمت نامشخص یا خالی"""
    assert ProductParser.clean_price("") == 0
    assert ProductParser.clean_price(None) == 0


def test_parse_product_item_mock():
    """تست ساختار پارسر روی دیتای شبیه‌سازی‌شده"""
    mock_html = """
    <div class="product-card">
        <a class="product-title" href="/product-123/samsung-a55">گوشی موبایل سامسونگ مدل Galaxy A55</a>
        <span class="product-price">۴۴,۹۹۹,۰۰۰ تومان</span>
    </div>
    """
    products = ProductParser.parse_product_list(mock_html)
    assert isinstance(products, list)
