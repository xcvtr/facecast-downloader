"""ChatDownloader для сохранения чата с facecast.net"""

import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    """Сообщение чата"""
    timestamp: str
    username: str
    message: str
    user_id: Optional[str] = None


class ChatDownloadError(Exception):
    """Ошибка скачивания чата"""
    pass


class ChatDownloader:
    """Скачивает и сохраняет чат с facecast.net"""
    
    BASE_URL = "https://facecast.net"
    TIMEOUT = 30
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://facecast.net/'
        })
    
    def download_chat(self, video_id: str, code: Optional[str] = None) -> List[ChatMessage]:
        """
        Скачивает историю чата для видео
        
        Args:
            video_id: Идентификатор видео
            code: Опциональный код доступа
            
        Returns:
            Список сообщений чата
            
        Raises:
            ChatDownloadError: Если не удалось скачать чат
        """
        # Пробуем различные API endpoints для получения чата
        chat_messages = []
        
        # Endpoint 1: Попытка получить чат через API
        try:
            chat_messages = self._try_api_endpoint(video_id, code)
            if chat_messages:
                return chat_messages
        except Exception:
            pass
        
        # Endpoint 2: Попытка получить чат через HTML страницу
        try:
            chat_messages = self._try_html_endpoint(video_id, code)
            if chat_messages:
                return chat_messages
        except Exception:
            pass
        
        # Если ничего не получилось, возвращаем пустой список
        # (чат может быть отключен или недоступен)
        return []
    
    def _try_api_endpoint(self, video_id: str, code: Optional[str]) -> List[ChatMessage]:
        """Пытается получить чат через API"""
        # Используем правильный API endpoint для получения данных события
        url = f"{self.BASE_URL}/api/event/{video_id}"
        params = {}
        if code:
            params['key'] = code
        
        try:
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                # Извлекаем чат из данных события
                if isinstance(data, dict) and 'chat' in data:
                    return self._parse_chat_data(data['chat'])
                # Если чат находится в другом месте структуры
                elif isinstance(data, dict) and 'messages' in data:
                    return self._parse_chat_data(data['messages'])
                # Пробуем распарсить всю структуру
                return self._parse_chat_data(data)
        except Exception as e:
            print(f"Ошибка при получении чата через API: {e}")
        
        return []
    
    def _try_html_endpoint(self, video_id: str, code: Optional[str]) -> List[ChatMessage]:
        """Пытается получить чат из HTML страницы"""
        url = f"{self.BASE_URL}/w/chat.html?{video_id}"
        if code:
            url += f"&key={code}"
        
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            if response.status_code == 200:
                # Пытаемся найти JSON данные в HTML
                html = response.text
                # Ищем данные чата в скриптах
                import re
                json_match = re.search(r'var\s+chatData\s*=\s*(\[.*?\]);', html, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                    return self._parse_chat_data(data)
        except Exception:
            pass
        
        return []
    
    def _parse_chat_data(self, data: any) -> List[ChatMessage]:
        """Парсит данные чата в список сообщений"""
        messages = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Пытаемся извлечь данные из различных возможных полей
                    timestamp = (item.get('timestamp') or 
                               item.get('time') or 
                               item.get('created_at') or 
                               item.get('date') or '')
                    
                    username = (item.get('username') or 
                              item.get('user') or 
                              item.get('name') or 
                              item.get('author') or 
                              item.get('from') or 
                              'Unknown')
                    
                    message_text = (item.get('message') or 
                                  item.get('text') or 
                                  item.get('content') or 
                                  item.get('body') or '')
                    
                    user_id = (item.get('user_id') or 
                             item.get('userId') or 
                             item.get('uid') or 
                             item.get('id'))
                    
                    # Создаем сообщение только если есть текст
                    if message_text:
                        message = ChatMessage(
                            timestamp=str(timestamp),
                            username=str(username),
                            message=str(message_text),
                            user_id=str(user_id) if user_id else None
                        )
                        messages.append(message)
        elif isinstance(data, dict):
            # Рекурсивно ищем массив сообщений в структуре
            if 'messages' in data:
                return self._parse_chat_data(data['messages'])
            elif 'chat' in data:
                return self._parse_chat_data(data['chat'])
            elif 'items' in data:
                return self._parse_chat_data(data['items'])
            elif 'data' in data:
                return self._parse_chat_data(data['data'])
        
        return messages
    
    def save_chat_txt(self, messages: List[ChatMessage], output_path: str):
        """
        Сохраняет чат в текстовый файл
        
        Args:
            messages: Список сообщений
            output_path: Путь для сохранения
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("Чат видео\n")
            f.write(f"Сохранено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Всего сообщений: {len(messages)}\n")
            f.write("="*60 + "\n\n")
            
            for msg in messages:
                timestamp = msg.timestamp if msg.timestamp else "??:??:??"
                f.write(f"[{timestamp}] {msg.username}: {msg.message}\n")
    
    def save_chat_json(self, messages: List[ChatMessage], output_path: str):
        """
        Сохраняет чат в JSON файл
        
        Args:
            messages: Список сообщений
            output_path: Путь для сохранения
        """
        data = {
            'saved_at': datetime.now().isoformat(),
            'message_count': len(messages),
            'messages': [
                {
                    'timestamp': msg.timestamp,
                    'username': msg.username,
                    'message': msg.message,
                    'user_id': msg.user_id
                }
                for msg in messages
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_chat_html(self, messages: List[ChatMessage], output_path: str):
        """
        Сохраняет чат в HTML файл
        
        Args:
            messages: Список сообщений
            output_path: Путь для сохранения
        """
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Чат видео</title>
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
            padding: 10px;
            margin-bottom: 10px;
            border-left: 3px solid #4CAF50;
            background-color: #f9f9f9;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .username {{
            font-weight: bold;
            color: #333;
        }}
        .text {{
            margin-top: 5px;
            color: #444;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Чат видео</h1>
        <p>Сохранено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Всего сообщений: {len(messages)}</p>
    </div>
    <div class="chat-container">
"""
        
        for msg in messages:
            timestamp = msg.timestamp if msg.timestamp else "??:??:??"
            html += f"""        <div class="message">
            <span class="timestamp">[{timestamp}]</span>
            <span class="username">{msg.username}</span>
            <div class="text">{msg.message}</div>
        </div>
"""
        
        html += """    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
