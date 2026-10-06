import arabic_reshaper
from bidi.algorithm import get_display

def farsi(text: str) -> str:
    """اصلاح جهت و نحوه نمایش متون فارسی"""
    return get_display(arabic_reshaper.reshape(str(text)))

def farsi_menu(message: str, choices: list):
    """ایجاد منوی تعاملی با گزینه‌های فارسی اصلاح شده"""
    import questionary
    # اصلاح هر گزینه و بازگرداندن یک دیکشنری برای questionary
    # که هم نمایش فارسی داشته باشد و هم مقدار اصلی را برگرداند
    choices_dict = {farsi(c): c for c in choices}
    
    selected_display = questionary.select(
        farsi(message), 
        choices=list(choices_dict.keys())
    ).ask()
    
    return choices_dict.get(selected_display)
