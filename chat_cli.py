import os
import sys
from gpt4all import GPT4All
import arabic_reshaper
from bidi.algorithm import get_display
from prompt_toolkit import prompt

def format_farsi(text):
    # اتصال حروف و اصلاح جهت برای نمایش
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def start_chat():
    # مخفی‌سازی هشدارهای سیستم (در صورت وجود)
    sys.stderr = open(os.devnull, 'w')
    print(format_farsi('در حال بارگذاری مدل 3B...'))
    model = GPT4All('Llama-3.2-3B-Instruct-Q4_K_M.gguf', model_path='.', device='cpu')
    sys.stderr = sys.__stderr__
    
    print('\n' + format_farsi('آماده چت! (برای خروج exit یا quit را تایپ کنید)') + '\n')
    
    system_prompt = "You are a helpful assistant. Always answer in Persian."
    
    with model.chat_session(system_prompt=system_prompt):
        while True:
            # ورودی (نمایش برچسب فارسی اصلاح شده)
            user_input = prompt(format_farsi('عبارت را وارد کنید') + ': ')
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # مدل ورودی را به صورت خام دریافت می‌کند (صحیح است)
            raw_response = model.generate(user_input, max_tokens=200, temp=0.1)
            
            # نمایش خروجی (اصلاح شده)
            # استفاده از دوقسمتی کردن برای جلوگیری از تداخل جهت نوشتار
            print(format_farsi('هوش مصنوعی: ') + format_farsi(raw_response) + '\n')

if __name__ == '__main__':
    start_chat()
