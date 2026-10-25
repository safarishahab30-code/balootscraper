from gpt4all import GPT4All

def farsi(text):
    return text

try:
    model = GPT4All('Llama-3.2-3B-Instruct-Q4_K_M.gguf', model_path='.', device='cpu')
    output = model.generate('What is 2+2? Answer only with the number.', max_tokens=5)
    print(farsi(f'خروجی تست مدل: {output}'))
except Exception as e:
    print(farsi(f'خطا در بارگذاری: {e}'))
