# در scraper/utils.py
import arabic_reshaper
from bidi.algorithm import get_display
from questionary import Choice, select
import questionary

def farsi(text):
    return get_display(arabic_reshaper.reshape(text))

def farsi_reshape_only(text):
    """فقط برای اصلاح فرم حروف در منوها (بدون تغییر ترتیب بیدی)"""
    if not text: return text
    return arabic_reshaper.reshape(text)
# در scraper/utils.py

from questionary import select, Choice
def farsi_menu(message, choices):
    """نمایش منوی فارسی تعاملی با questionary سازگار با رشته و دیکشنری."""
    formatted_choices = []
    
    for c in choices:
        if isinstance(c, dict):
            formatted_choices.append(
                questionary.Choice(
                    title=farsi(c.get("name", "")),
                    value=c.get("value")
                )
            )
        else:
            formatted_choices.append(farsi(str(c)))

    return questionary.select(
        farsi(message),
        choices=formatted_choices
    ).ask()
