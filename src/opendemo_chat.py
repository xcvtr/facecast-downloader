"""Модуль для извлечения чата с opendemo.ru"""

import time
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class OpendemoChat:
    """Извлекает чат с opendemo.ru используя Selenium"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: Запускать браузер в фоновом режиме
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium не установлен. Установите: pip install selenium"
            )
        
        self.headless = headless
    
    def extract_chat(self, video_id: str, code: Optional[str] = None, 
                    wait_time: int = 15) -> List[Dict[str, str]]:
        """
        Извлекает чат с opendemo.ru
        
        Args:
            video_id: ID видео
            code: Код доступа (опционально)
            wait_time: Время ожидания загрузки сообщений (секунды)
            
        Returns:
            Список сообщений в формате [{'author': '...', 'text': '...', 'time': '...'}, ...]
        """
        url = f"https://opendemo.ru/live?id={video_id}"
        if code:
            url += f"&code={code}"
        
        print(f"Извлечение чата с: {url}")
        
        # Настройка Chrome
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = None
        messages = []
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Ждем iframe с facecast
            wait = WebDriverWait(driver, 15)
            iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#facecast-holder iframe"))
            )
            
            # Переключаемся на iframe
            driver.switch_to.frame(iframe)
            
            # Ждем виджет чата
            chat_widget = wait.until(
                EC.presence_of_element_located((By.ID, "hypercomments_widget"))
            )
            
            # Даем время на загрузку сообщений
            print(f"Ожидание загрузки сообщений ({wait_time} сек)...")
            time.sleep(wait_time)
            
            # Извлекаем сообщения через JavaScript
            js_script = """
            var widget = document.getElementById('hypercomments_widget');
            var messages = [];
            
            if (widget) {
                var elements = widget.querySelectorAll('div[class*="Message"]');
                
                for (var i = 0; i < elements.length; i++) {
                    var elem = elements[i];
                    var text = elem.innerText || elem.textContent;
                    
                    if (text && text.trim().length > 5) {
                        messages.push(text.trim());
                    }
                }
            }
            
            return messages;
            """
            
            raw_messages = driver.execute_script(js_script)
            
            # Парсим сообщения
            messages = self._parse_messages(raw_messages)
            
            print(f"✓ Извлечено сообщений: {len(messages)}")
            
        except Exception as e:
            print(f"✗ Ошибка при извлечении чата: {e}")
            
        finally:
            if driver:
                driver.quit()
        
        return messages
    
    def _parse_messages(self, raw_messages: List[str]) -> List[Dict[str, str]]:
        """Парсит сырые сообщения в структурированный формат"""
        parsed = []
        seen = set()
        
        for raw in raw_messages:
            # Пропускаем дубликаты
            if raw in seen:
                continue
            seen.add(raw)
            
            # Пытаемся извлечь время, автора и текст
            # Формат: "15:00Антон Середкин (Базис)МодераторТекст сообщения"
            
            # Ищем время в начале (HH:MM)
            time_match = re.match(r'^(\d{1,2}:\d{2})', raw)
            time_str = time_match.group(1) if time_match else ""
            
            # Убираем время из текста
            text = raw[len(time_str):] if time_str else raw
            
            # Пытаемся найти автора (обычно в начале, может содержать скобки)
            # Ищем паттерн: "Имя Фамилия (Компания)" или просто "Имя Фамилия"
            author_match = re.match(r'^([А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+)*(?:\s*\([^)]+\))?)', text)
            author = author_match.group(1).strip() if author_match else "Unknown"
            
            # Убираем автора из текста
            if author != "Unknown":
                text = text[len(author):].strip()
            
            # Убираем "Модератор" если есть
            text = re.sub(r'^Модератор\s*', '', text)
            
            # Убираем эмодзи в конце
            text = re.sub(r'[👍👎❤️🤩🔥😍👋😋😆🥰🤣🤔🤯😱🤬😢😈🤷‍♂️💯🎉💔🤝🏆🗿]+$', '', text).strip()
            
            # Добавляем только если есть текст
            if text and len(text) > 3:
                parsed.append({
                    'time': time_str,
                    'author': author,
                    'text': text
                })
        
        return parsed
    
    def save_txt(self, messages: List[Dict[str, str]], output_path: str):
        """Сохраняет чат в текстовый файл"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("Чат с opendemo.ru\n")
            f.write(f"Сохранено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего сообщений: {len(messages)}\n")
            f.write("=" * 80 + "\n\n")
            
            for msg in messages:
                time_str = f"[{msg['time']}] " if msg['time'] else ""
                f.write(f"{time_str}{msg['author']}:\n")
                f.write(f"{msg['text']}\n\n")
        
        print(f"✓ Чат сохранен: {output_path}")
    
    def save_json(self, messages: List[Dict[str, str]], output_path: str):
        """Сохраняет чат в JSON файл"""
        data = {
            'saved_at': datetime.now().isoformat(),
            'message_count': len(messages),
            'messages': messages
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ JSON сохранен: {output_path}")
    
    def save_html(self, messages: List[Dict[str, str]], output_path: str):
        """Сохраняет чат в HTML файл"""
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Чат opendemo.ru</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .chat-container {{
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .message {{
            padding: 15px;
            margin-bottom: 15px;
            border-left: 3px solid #4CAF50;
            background-color: #f9f9f9;
        }}
        .message-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .author {{
            font-weight: bold;
            color: #333;
        }}
        .time {{
            color: #666;
            font-size: 0.9em;
        }}
        .text {{
            color: #444;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Чат opendemo.ru</h1>
        <p>Сохранено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Всего сообщений: {len(messages)}</p>
    </div>
    <div class="chat-container">
"""
        
        for msg in messages:
            time_str = msg['time'] if msg['time'] else ''
            author = msg['author']
            text = msg['text'].replace('\n', '<br>')
            
            html += f"""        <div class="message">
            <div class="message-header">
                <span class="author">{author}</span>
                <span class="time">{time_str}</span>
            </div>
            <div class="text">{text}</div>
        </div>
"""
        
        html += """    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ HTML сохранен: {output_path}")
