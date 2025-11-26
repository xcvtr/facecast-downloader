"""VideoDownloader для скачивания видео сегментов"""

import os
import time
import requests
from typing import List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .progress import ProgressTracker


@dataclass
class DownloadResult:
    """Результат скачивания"""
    success: bool
    output_path: Optional[str]
    error_message: Optional[str]


class DownloadError(Exception):
    """Ошибка скачивания"""
    pass


class VideoDownloader:
    """Скачивает видео сегменты и объединяет их"""
    
    RETRY_COUNT = 3
    RETRY_DELAY = 1  # секунды
    TIMEOUT = 30
    DEFAULT_WORKERS = 5
    
    def __init__(self, max_workers: int = DEFAULT_WORKERS):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.max_workers = max_workers
        self.progress_lock = threading.Lock()
    
    def download_segments(self, segment_urls: List[str], output_path: str) -> DownloadResult:
        """
        Скачивает все сегменты параллельно и объединяет их в один файл
        
        Args:
            segment_urls: Список URL сегментов
            output_path: Путь для сохранения результата
            
        Returns:
            DownloadResult с информацией о результате
        """
        if not segment_urls:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message="Список сегментов пуст"
            )
        
        print(f"\nНайдено сегментов: {len(segment_urls)}")
        print(f"Параллельных потоков: {self.max_workers}")
        progress = ProgressTracker(len(segment_urls), "Скачивание сегментов")
        
        # Словарь для хранения скачанных сегментов с их индексами
        segments_data = {}
        error_message = None
        
        try:
            # Скачиваем сегменты параллельно
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Создаем задачи для скачивания
                future_to_index = {
                    executor.submit(self.download_segment, url): i 
                    for i, url in enumerate(segment_urls)
                }
                
                # Обрабатываем завершенные задачи
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        segment_data = future.result()
                        segments_data[index] = segment_data
                        
                        with self.progress_lock:
                            progress.update()
                            
                    except DownloadError as e:
                        error_message = f"Не удалось скачать сегмент {index+1}/{len(segment_urls)}: {e}"
                        # Отменяем оставшиеся задачи
                        for f in future_to_index:
                            f.cancel()
                        break
            
            if error_message:
                return DownloadResult(
                    success=False,
                    output_path=None,
                    error_message=error_message
                )
            
            # Записываем сегменты в правильном порядке
            print("\nОбъединение сегментов...")
            with open(output_path, 'wb') as output_file:
                for i in range(len(segment_urls)):
                    if i in segments_data:
                        output_file.write(segments_data[i])
            
            progress.complete(f"Видео успешно сохранено: {output_path}")
            
            return DownloadResult(
                success=True,
                output_path=os.path.abspath(output_path),
                error_message=None
            )
            
        except IOError as e:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message=f"Ошибка записи файла: {e}"
            )
    
    def download_segment(self, url: str, retry_count: int = RETRY_COUNT) -> bytes:
        """
        Скачивает один сегмент с повторными попытками
        
        Args:
            url: URL сегмента
            retry_count: Количество попыток
            
        Returns:
            Данные сегмента
            
        Raises:
            DownloadError: Если не удалось скачать после всех попыток
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                return response.content
                
            except requests.RequestException as e:
                last_error = e
                if attempt < retry_count - 1:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                continue
        
        raise DownloadError(
            f"Не удалось скачать сегмент после {retry_count} попыток: {last_error}"
        )
    
    def download_direct(self, url: str, output_path: str) -> DownloadResult:
        """
        Скачивает видео по прямой ссылке
        
        Args:
            url: Прямая ссылка на видео
            output_path: Путь для сохранения
            
        Returns:
            DownloadResult с информацией о результате
        """
        print(f"\nСкачивание видео по прямой ссылке...")
        
        try:
            response = self.session.get(url, stream=True, timeout=self.TIMEOUT)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f:
                if total_size > 0:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percentage = (downloaded / total_size) * 100
                            print(f"\rПрогресс: {percentage:.1f}%", end='')
                    print()
                else:
                    f.write(response.content)
            
            print(f"✓ Видео успешно сохранено: {output_path}")
            
            return DownloadResult(
                success=True,
                output_path=os.path.abspath(output_path),
                error_message=None
            )
            
        except requests.RequestException as e:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message=f"Ошибка скачивания: {e}"
            )
        except IOError as e:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message=f"Ошибка записи файла: {e}"
            )
