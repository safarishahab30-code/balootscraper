# در scraper/utils.py
import arabic_reshaper
from bidi.algorithm import get_display
from questionary import Choice, select

def farsi(text):
    return get_display(arabic_reshaper.reshape(text))

def farsi_reshape_only(text):
    """فقط برای اصلاح فرم حروف در منوها (بدون تغییر ترتیب بیدی)"""
    if not text: return text
    return arabic_reshaper.reshape(text)
# در scraper/utils.py

from questionary import select, Choice

def farsi_menu(message, choices):
    """منوی فارسی‌ساز که با شیء Choice هم سازگار است"""
    processed_choices = []
    for c in choices:
        if isinstance(c, Choice):
            # اگر Choice است، عنوان آن را فارسی کن و دوباره بساز
            processed_choices.append(Choice(farsi(c.title), value=c.value))
        else:
            # اگر رشته است، مثل قبل فارسی کن
            processed_choices.append(farsi(c))
            
    return select(
        farsi(message),
        choices=processed_choices
    ).ask()