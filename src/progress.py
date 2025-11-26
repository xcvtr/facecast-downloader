"""ProgressTracker для отображения прогресса скачивания"""

import sys
from typing import Optional


class ProgressTracker:
    """Отслеживает и отображает прогресс скачивания"""
    
    def __init__(self, total: int, description: str = "Скачивание"):
        """
        Инициализирует трекер прогресса
        
        Args:
            total: Общее количество элементов
            description: Описание процесса
        """
        self.total = total
        self.current = 0
        self.description = description
        
    def update(self, current: Optional[int] = None):
        """
        Обновляет отображение прогресса
        
        Args:
            current: Текущее значение (если None, увеличивает на 1)
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        percentage = self._calculate_percentage()
        self._display(percentage)
    
    def _calculate_percentage(self) -> float:
        """
        Вычисляет процент выполнения
        
        Returns:
            Процент от 0 до 100
        """
        if self.total == 0:
            return 100.0
        
        percentage = (self.current / self.total) * 100
        return min(100.0, max(0.0, percentage))
    
    def _display(self, percentage: float):
        """
        Отображает прогресс в консоли
        
        Args:
            percentage: Процент выполнения
        """
        bar_length = 40
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(
            f'\r{self.description}: [{bar}] {self.current}/{self.total} ({percentage:.1f}%)'
        )
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write('\n')
            sys.stdout.flush()
    
    def complete(self, message: str = "Завершено успешно!"):
        """
        Отображает сообщение о завершении
        
        Args:
            message: Сообщение о завершении
        """
        print(f"\n✓ {message}")
