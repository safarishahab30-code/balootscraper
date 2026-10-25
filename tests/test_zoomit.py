import os
import pytest
from bs4 import BeautifulSoup
from scraper.utils import farsi

def test_zoomit_html_parsing():
    if not os.path.exists('debug_zoomit.html'):
        pytest.skip(farsi("فایل debug_zoomit.html موجود نیست"))

    with open('debug_zoomit.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    container = soup.select_one('[data-testid="list-data-renderer"]')
    products = container.select('a') if container else []

    print(farsi(f"تعداد کل لینک‌های یافت شده: {len(products)}"))
    if products:
        print(farsi(f"لینک نمونه: {products[0].get('href')}"))
