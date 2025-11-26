"""Управление файловой системой для сохранения видео"""

import os
from pathlib import Path
from typing import Optional


class FileManager:
    """Управляет сохранением файлов"""
    
    @staticmethod
    def ensure_directory(directory: str) -> None:
        """
        Проверяет существование директории и создает её при необходимости
        
        Args:
            directory: Путь к директории
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def generate_output_path(video_id: str, output_dir: str, extension: str = "mp4") -> str:
        """
        Генерирует путь для сохранения файла на основе video_id
        
        Args:
            video_id: Идентификатор видео
            output_dir: Директория для сохранения
            extension: Расширение файла
            
        Returns:
            Полный путь к файлу (с разрешением конфликтов)
        """
        FileManager.ensure_directory(output_dir)
        
        base_filename = f"{video_id}.{extension}"
        output_path = os.path.join(output_dir, base_filename)
        
        # Если файл существует, добавляем числовой суффикс
        if os.path.exists(output_path):
            counter = 1
            while True:
                new_filename = f"{video_id}_{counter}.{extension}"
                output_path = os.path.join(output_dir, new_filename)
                if not os.path.exists(output_path):
                    break
                counter += 1
        
        return output_path
    
    @staticmethod
    def get_absolute_path(path: str) -> str:
        """
        Возвращает абсолютный путь
        
        Args:
            path: Путь (может быть относительным или абсолютным)
            
        Returns:
            Абсолютный путь
        """
        return os.path.abspath(path)
    
    @staticmethod
    def validate_directory(directory: str) -> bool:
        """
        Проверяет, является ли путь валидной директорией
        
        Args:
            directory: Путь к директории
            
        Returns:
            True если директория существует или может быть создана
        """
        try:
            # Пытаемся создать директорию если её нет
            FileManager.ensure_directory(directory)
            return os.path.isdir(directory)
        except (OSError, PermissionError):
            return False
