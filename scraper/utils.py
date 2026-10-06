import arabic_reshaper
from bidi.algorithm import get_display

def farsi(text: str) -> str:
    """اصلاح جهت و نحوه نمایش متون فارسی"""
    return get_display(arabic_reshaper.reshape(str(text)))

from questionary import Choice

def farsi_menu(items):
    # items ورودی لیستی از تاپل‌هاست: [('متن_فارسی', 'مقدار_خروجی'), ...]
    return [Choice(farsi(text), value=value) for text, value in items]

    return choices_dict.get(selected_display)
