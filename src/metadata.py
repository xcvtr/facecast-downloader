"""VideoMetadataExtractor для получения URL видеопотока с facecast.net"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """Информация о видео"""
    video_id: str
    stream_url: str
    stream_type: str  # 'direct' или 'm3u8'


class MetadataExtractionError(Exception):
    """Ошибка извлечения метаданных"""
    pass


class VideoMetadataExtractor:
    """Извлекает метаданные видео с facecast.net"""
    
    BASE_URL = "https://facecast.net"
    TIMEOUT = 30
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_stream_url(self, video_id: str) -> VideoInfo:
        """
        Получает HTML-страницу и извлекает URL видеопотока
        
        Args:
            video_id: Идентификатор видео
            
        Returns:
            VideoInfo: Информация о видеопотоке
            
        Raises:
            MetadataExtractionError: Если не удалось извлечь URL потока
        """
        url = f"{self.BASE_URL}/w/{video_id}"
        
        try:
            response = self.session.get(url, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            raise MetadataExtractionError(
                f"Не удалось получить страницу видео: {e}"
            )
        
        html_content = response.text
        stream_url = self._parse_stream_url(html_content)
        
        if not stream_url:
            raise MetadataExtractionError(
                "Не удалось найти URL видеопотока на странице. "
                "Возможно, видео недоступно или удалено."
            )
        
        stream_type = self._detect_stream_type(stream_url)
        
        return VideoInfo(
            video_id=video_id,
            stream_url=stream_url,
            stream_type=stream_type
        )
    
    def _parse_stream_url(self, html_content: str) -> Optional[str]:
        """
        Парсит HTML и извлекает URL видеопотока
        
        Ищет в различных местах:
        - В TEMPLATE_EVENT_DATA и GET_SERVERS переменных
        - В script tags с JSON данными
        - В data-атрибутах video элементов
        """
        # Специальная обработка для facecast.net
        # Ищем TEMPLATE_EVENT_DATA и GET_SERVERS
        event_data_match = re.search(r'var TEMPLATE_EVENT_DATA = JSON\.parse\(\'({[^\']+})\'\);', html_content)
        servers_match = re.search(r'var GET_SERVERS = JSON\.parse\(\'(\[[^\]]+\])\'\);', html_content)
        
        if event_data_match and servers_match:
            try:
                # Декодируем JSON данные
                event_data_str = event_data_match.group(1)
                # Заменяем экранированные кавычки
                event_data_str = event_data_str.replace('\\', '')
                event_data = json.loads(event_data_str)
                
                servers_str = servers_match.group(1)
                servers_str = servers_str.replace('\\', '')
                servers = json.loads(servers_str)
                
                # Извлекаем event_id (это поле 'id' в TEMPLATE_EVENT_DATA)
                event_id = event_data.get('id')
                
                if event_id and servers:
                    # Выбираем первый доступный CDN сервер
                    server = None
                    for s in servers:
                        if s.get('cdn') == 1:  # Предпочитаем CDN
                            server = s.get('src')
                            break
                    
                    if not server and servers:
                        server = servers[0].get('src')
                    
                    if server:
                        # Строим URL для M3U8 плейлиста
                        # Формат: https://{server}/public/{event_id}.m3u8
                        m3u8_url = f"https://{server}/public/{event_id}.m3u8"
                        return m3u8_url
                        
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                # Если не удалось распарсить, продолжаем другими методами
                pass
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Поиск в script tags с JSON
        for script in soup.find_all('script'):
            script_text = script.string
            if script_text:
                # Ищем URL с .m3u8 или прямые ссылки на видео
                m3u8_match = re.search(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', script_text)
                if m3u8_match:
                    return m3u8_match.group(0)
        
        # Поиск в video элементах
        video_tag = soup.find('video')
        if video_tag:
            if video_tag.get('src'):
                return video_tag['src']
            source_tag = video_tag.find('source')
            if source_tag and source_tag.get('src'):
                return source_tag['src']
        
        return None
    
    def _detect_stream_type(self, stream_url: str) -> str:
        """
        Определяет формат потока по URL
        
        Args:
            stream_url: URL видеопотока
            
        Returns:
            'direct' или 'm3u8'
        """
        if '.m3u8' in stream_url.lower():
            return 'm3u8'
        return 'direct'
