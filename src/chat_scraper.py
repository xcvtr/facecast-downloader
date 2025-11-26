"""Модуль для извлечения чата с использованием браузерной автоматизации"""

import time
from typing import List, Optional
from dataclasses import dataclass

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@dataclass
class ChatMessage:
    """Сообщение чата"""
    timestamp: str
    username: str
    message: str
    user_id: Optional[str] = None


class ChatScraperError(Exception):
    """Ошибка скрапинга чата"""
    pass


class ChatScraper:
    """Извлекает чат используя Selenium"""
    
    def __init__(self, headless: bool = True):
        """
        Args:
            headless: Запускать браузер в фоновом режиме
        """
        if not SELENIUM_AVAILABLE:
            raise ChatScraperError(
                "Selenium не установлен. Установите: pip install selenium webdriver-manager"
            )
        
        self.headless = headless
    
    def scrape_chat(self, video_id: str, code: Optional[str] = None, timeout: int = 15) -> List[ChatMessage]:
        """
        Извлекает чат с страницы видео
        
        Args:
            video_id: ID видео
            code: Код доступа (опционально)
            timeout: Таймаут ожидания загрузки чата (секунды)
            
        Returns:
            Список сообщений чата
            
        Raises:
            ChatScraperError: Если не удалось извлечь чат
        """
        url = f"https://facecast.net/w/{video_id}"
        if code:
            url += f"?key={code}"
        
        print(f"Запуск браузера для извлечения чата...")
        print(f"URL: {url}")
        
        driver = None
        try:
            # Настройка Chrome
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Создаем драйвер
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            print("Ожидание загрузки виджета чата...")
            
            # Ждем загрузки виджета HyperComments
            wait = WebDriverWait(driver, timeout)
            
            try:
                # Ждем появления контейнера чата
                chat_container = wait.until(
                    EC.presence_of_element_located((By.ID, "hypercomments_widget"))
                )
                print("✓ Виджет чата найден")
                
                # Даем время на загрузку сообщений
                time.sleep(5)
                
                # Делаем скриншот для отладки
                try:
                    driver.save_screenshot(f"chat_screenshot_{video_id}.png")
                    print(f"✓ Скриншот сохранен: chat_screenshot_{video_id}.png")
                except:
                    pass
                
                # Сохраняем HTML для анализа
                try:
                    with open(f"chat_page_{video_id}.html", 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"✓ HTML сохранен: chat_page_{video_id}.html")
                except:
                    pass
                
                # Пробуем найти сообщения
                messages = self._extract_messages(driver)
                
                if messages:
                    print(f"✓ Извлечено сообщений: {len(messages)}")
                else:
                    print("⚠ Сообщения не найдены в виджете")
                    # Пробуем альтернативные селекторы
                    messages = self._extract_messages_alternative(driver)
                    if messages:
                        print(f"✓ Извлечено сообщений (альтернативный метод): {len(messages)}")
                
                return messages
                    
            except TimeoutException:
                print("⚠ Виджет чата не загрузился за отведенное время")
                return []
                
        except Exception as e:
            raise ChatScraperError(f"Ошибка при извлечении чата: {e}")
            
        finally:
            if driver:
                driver.quit()
                print("Браузер закрыт")
    
    def _extract_messages(self, driver) -> List[ChatMessage]:
        """Извлекает сообщения используя основные селекторы HyperComments"""
        messages = []
        
        try:
            # Селекторы для HyperComments
            message_elements = driver.find_elements(By.CSS_SELECTOR, ".hc__message, .hc-message, [class*='message']")
            
            for elem in message_elements:
                try:
                    # Пытаемся извлечь данные сообщения
                    username = self._safe_find_text(elem, [
                        ".hc__message__author",
                        ".hc-message-author",
                        ".hc__author",
                        "[class*='author']"
                    ])
                    
                    message_text = self._safe_find_text(elem, [
                        ".hc__message__text",
                        ".hc-message-text",
                        ".hc__text",
                        "[class*='text']",
                        "[class*='content']"
                    ])
                    
                    timestamp = self._safe_find_text(elem, [
                        ".hc__message__time",
                        ".hc-message-time",
                        ".hc__time",
                        "[class*='time']",
                        "[class*='date']"
                    ])
                    
                    if username and message_text:
                        messages.append(ChatMessage(
                            timestamp=timestamp or "",
                            username=username,
                            message=message_text
                        ))
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Ошибка при извлечении сообщений: {e}")
        
        return messages
    
    def _extract_messages_alternative(self, driver) -> List[ChatMessage]:
        """Альтернативный метод извлечения сообщений"""
        messages = []
        
        try:
            # Пробуем найти iframe с чатом
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    
                    # Пробуем найти сообщения внутри iframe
                    message_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='message'], [class*='comment']")
                    
                    if message_elements:
                        print(f"Найдено {len(message_elements)} элементов в iframe")
                        
                        for elem in message_elements:
                            try:
                                text = elem.text.strip()
                                if text and len(text) > 5:  # Минимальная длина сообщения
                                    messages.append(ChatMessage(
                                        timestamp="",
                                        username="Unknown",
                                        message=text
                                    ))
                            except:
                                continue
                    
                    driver.switch_to.default_content()
                    
                    if messages:
                        break
                        
                except:
                    driver.switch_to.default_content()
                    continue
                    
        except Exception as e:
            print(f"Ошибка при альтернативном извлечении: {e}")
        
        return messages
    
    def _safe_find_text(self, element, selectors: List[str]) -> str:
        """Безопасно находит текст по списку селекторов"""
        for selector in selectors:
            try:
                elem = element.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return ""
