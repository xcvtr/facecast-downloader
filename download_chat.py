#!/usr/bin/env python3
"""Финальный тест извлечения чата с opendemo.ru"""

import sys
from src.opendemo_chat import OpendemoChat, SELENIUM_AVAILABLE

def main():
    if not SELENIUM_AVAILABLE:
        print("✗ Selenium не установлен!")
        print("Установите: pip install selenium")
        return
    
    # Проверка на help
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print("=" * 80)
        print("Извлечение чата с opendemo.ru")
        print("=" * 80)
        print("\nИспользование:")
        print("  python download_chat.py <video_id> <code>")
        print("\nПримеры:")
        print("  python download_chat.py zfvfh8 1")
        print("  python download_chat.py abc123 mycode")
        print("\nРезультат:")
        print("  Создаст 3 файла:")
        print("  - <video_id>_chat.txt  - текстовый формат")
        print("  - <video_id>_chat.json - JSON формат")
        print("  - <video_id>_chat.html - HTML формат")
        print("\nПодробнее: README.md")
        print("=" * 80)
        return
    
    # Параметры
    if len(sys.argv) > 2:
        video_id = sys.argv[1]
        code = sys.argv[2]
    elif len(sys.argv) > 1:
        video_id = sys.argv[1]
        code = None
    else:
        print("Использование: python download_chat.py <video_id> <code>")
        print("Пример: python download_chat.py zfvfh8 1")
        print("\nДля справки: python download_chat.py --help")
        return
    
    print("=" * 80)
    print("Извлечение чата с opendemo.ru")
    print("=" * 80)
    print(f"\nVideo ID: {video_id}")
    if code:
        print(f"Code: {code}")
    print()
    
    # Создаем экстрактор
    extractor = OpendemoChat(headless=True)
    
    # Извлекаем чат
    messages = extractor.extract_chat(video_id, code, wait_time=15)
    
    if messages:
        print(f"\n{'=' * 80}")
        print(f"Извлечено сообщений: {len(messages)}")
        print('=' * 80)
        
        # Показываем первые 10
        print("\nПервые 10 сообщений:")
        print("-" * 80)
        for i, msg in enumerate(messages[:10], 1):
            time_str = f"[{msg['time']}] " if msg['time'] else ""
            print(f"\n{i}. {time_str}{msg['author']}:")
            print(f"   {msg['text'][:200]}")
        
        # Сохраняем в разных форматах
        print(f"\n{'=' * 80}")
        print("Сохранение...")
        print('=' * 80)
        
        extractor.save_txt(messages, f"{video_id}_chat.txt")
        extractor.save_json(messages, f"{video_id}_chat.json")
        extractor.save_html(messages, f"{video_id}_chat.html")
        
        print(f"\n{'=' * 80}")
        print("✓ Готово!")
        print('=' * 80)
    else:
        print("\n⚠ Чат не найден или пуст")

if __name__ == "__main__":
    main()
