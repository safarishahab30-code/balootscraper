from scraper.utils import farsi
import os
from gpt4all import GPT4All

# مشخص کردن مسیر دقیق فایل مدل در پوشه پروژه
# تغییر در فایل scraper/ai.py
model = GPT4All("Llama-3.2-3B-Instruct-Q4_K_M.gguf", model_path="C:/webscrapper/balootscraper")


class BookAIAssistant:
    def __init__(self, model_filename="Llama-3.2-1B-Instruct-Q4_K_M.gguf"):
        """
        بارگذاری مدل فقط یک‌بار در زمان ایجاد شیء (Instantiate) 
        برای جلوگیری از تأخیر بارگذاری در هر درخواست.
        """
        # مطمئن شو فایل مدل در پوشه پروژه است یا مسیر کامل بده
        self.model_filename = model_filename
        try:
            self.model = GPT4All(model_name=self.model_filename)
        except Exception as e:
            self.model = None
            print(farsi(f"خطا در بارگذاری مدل محلی: {e}"))

    def get_recommendation(self, user_query: str) -> str:
        """پاسخ به پرسش‌های عمومی با استفاده از مدل محلی"""
        if not self.model:
            return farsi("مدل هوش مصنوعی در دسترس نیست.")
        
        try:
            with self.model.chat_session():
                response = self.model.generate(user_query, max_tokens=200)
                return response
        except Exception as e:
            return farsi(f"خطا در تولید پاسخ: {e}")

    def analyze_books(self, books_data: list[dict], user_query: str) -> str:
        """ارسال لیست کتاب‌ها همراه با پرسش کاربر به مدل"""
        if not self.model:
            return farsi("مدل هوش مصنوعی در دسترس نیست.")
            
        context = f"لیست کتاب‌های موجود:\n{books_data}\n\nپرسش کاربر: {user_query}"
        
        try:
            with self.model.chat_session():
                response = self.model.generate(context, max_tokens=200)
                return response
        except Exception as e:
            return farsi(f"خطا در تحلیل داده‌ها: {e}")
