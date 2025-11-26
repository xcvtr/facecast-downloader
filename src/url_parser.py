"""URLParser для извлечения video_id из URL facecast.net"""

import re
from typing import Optional


class URLParseError(Exception):
    """Ошибка парсинга URL"""
    pass


class URLParser:
    """Парсер URL для извлечения video_id из facecast.net"""
    
    FACECAST_PATTERN = r'^https?://(?:www\.)?facecast\.net/w/([a-zA-Z0-9_-]+)/?$'
    
    def parse(self, url: str) -> str:
        """
        Извлекает video_id из URL facecast.net
        
        Args:
            url: URL видео на facecast.net
            
        Returns:
            video_id: Идентификатор видео
            
        Raises:
            URLParseError: Если URL имеет неверный формат
        """
        if not url or not isinstance(url, str):
            raise URLParseError("URL должен быть непустой строкой")
        
        match = re.match(self.FACECAST_PATTERN, url.strip())
        
        if not match:
            raise URLParseError(
                f"Неверный формат URL. Ожидается: https://facecast.net/w/{{video_id}}, "
                f"получено: {url}"
            )
        
        return match.group(1)
