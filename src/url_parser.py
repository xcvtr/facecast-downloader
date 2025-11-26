"""URLParser для извлечения video_id из URL facecast.net и opendemo.ru"""

import re
from typing import Optional


class URLParseError(Exception):
    """Ошибка парсинга URL"""
    pass


class URLParser:
    """Парсер URL для извлечения video_id из facecast.net и opendemo.ru"""
    
    FACECAST_PATTERN = r'^https?://(?:www\.)?facecast\.net/w/([a-zA-Z0-9_-]+)/?$'
    OPENDEMO_PATTERN = r'^https?://(?:www\.)?opendemo\.ru/live\?id=([a-zA-Z0-9_-]+)(?:&code=([a-zA-Z0-9_-]+))?$'
    
    def parse(self, url: str) -> tuple:
        """
        Извлекает video_id и опциональный code из URL facecast.net или opendemo.ru
        
        Args:
            url: URL видео на facecast.net или opendemo.ru
            
        Returns:
            tuple: (video_id, code) где code может быть None
            
        Raises:
            URLParseError: Если URL имеет неверный формат
        """
        if not url or not isinstance(url, str):
            raise URLParseError("URL должен быть непустой строкой")
        
        url = url.strip()
        
        # Проверяем opendemo.ru
        match = re.match(self.OPENDEMO_PATTERN, url)
        if match:
            video_id = match.group(1)
            code = match.group(2) if match.lastindex >= 2 else None
            return (video_id, code)
        
        # Проверяем facecast.net
        match = re.match(self.FACECAST_PATTERN, url)
        if match:
            return (match.group(1), None)
        
        raise URLParseError(
            f"Неверный формат URL. Ожидается: https://facecast.net/w/{{video_id}} "
            f"или https://opendemo.ru/live?id={{video_id}}&code={{code}}, "
            f"получено: {url}"
        )
