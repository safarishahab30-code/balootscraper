from bs4 import BeautifulSoup

with open('debug_zoomit.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), "html.parser")

container = soup.select_one('[data-testid="list-data-renderer"]')
# بررسی وجود محصولات (مثلاً پیدا کردن تگ لینک محصول)
products = container.select('a') if container else []

print((f"تعداد کل لینک‌های یافت شده: {len(products)}"))
if products:
    print(farsi(f"لینک نمونه: {products[0].get('href')}"))
