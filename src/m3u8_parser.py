"""M3U8Parser для парсинга HLS плейлистов"""

import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse


class M3U8ParseError(Exception):
    """Ошибка парсинга M3U8"""
    pass


class M3U8Parser:
    """Парсер M3U8 плейлистов"""
    
    def parse(self, m3u8_content: str, base_url: str) -> List[str]:
        """
        Парсит M3U8 плейлист и возвращает список URL сегментов
        
        Args:
            m3u8_content: Содержимое M3U8 файла
            base_url: Базовый URL для преобразования относительных путей
            
        Returns:
            Список абсолютных URL сегментов
            
        Raises:
            M3U8ParseError: Если не удалось распарсить плейлист
        """
        if not m3u8_content:
            raise M3U8ParseError("M3U8 содержимое пустое")
        
        lines = m3u8_content.strip().split('\n')
        segment_urls = []
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('#'):
                continue
            
            # Это URL сегмента
            absolute_url = self._resolve_url(line, base_url)
            segment_urls.append(absolute_url)
        
        if not segment_urls:
            raise M3U8ParseError("В M3U8 плейлисте не найдено сегментов")
        
        return segment_urls
    
    def _resolve_url(self, url: str, base_url: str) -> str:
        """
        Преобразует относительный URL в абсолютный
        
        Args:
            url: URL (может быть относительным или абсолютным)
            base_url: Базовый URL
            
        Returns:
            Абсолютный URL
        """
        # Если URL уже абсолютный, возвращаем как есть
        if url.startswith('http://') or url.startswith('https://'):
            return url
        
        # Преобразуем относительный URL в абсолютный
        return urljoin(base_url, url)
    
    def select_best_quality(self, master_playlist: str) -> str:
        """
        Выбирает плейлист с наивысшим качеством из master playlist
        
        Args:
            master_playlist: Содержимое master M3U8 плейлиста
            
        Returns:
            URL плейлиста с наивысшим качеством
            
        Raises:
            M3U8ParseError: Если не удалось найти варианты качества
        """
        lines = master_playlist.strip().split('\n')
        
        best_bandwidth = 0
        best_url = None
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Ищем строки с #EXT-X-STREAM-INF
            if line.startswith('#EXT-X-STREAM-INF:'):
                # Извлекаем bandwidth
                bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
                if bandwidth_match:
                    bandwidth = int(bandwidth_match.group(1))
                    
                    # Следующая строка должна содержать URL
                    if i + 1 < len(lines):
                        url = lines[i + 1].strip()
                        if url and not url.startswith('#'):
                            if bandwidth > best_bandwidth:
                                best_bandwidth = bandwidth
                                best_url = url
            
            i += 1
        
        if not best_url:
            raise M3U8ParseError(
                "Не удалось найти варианты качества в master плейлисте"
            )
        
        return best_url
    
    def is_master_playlist(self, m3u8_content: str) -> bool:
        """
        Проверяет, является ли плейлист master playlist
        
        Args:
            m3u8_content: Содержимое M3U8 файла
            
        Returns:
            True если это master playlist, False если обычный
        """
        return '#EXT-X-STREAM-INF:' in m3u8_content
