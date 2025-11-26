# Facecast Video Downloader

Инструмент для скачивания видео с платформ facecast.net и opendemo.ru с поддержкой параллельного скачивания сегментов и извлечения чата.

## Возможности

- ✅ Скачивание видео по URL с facecast.net и opendemo.ru
- ✅ Поддержка защищенных видео с кодом доступа (opendemo.ru)
- ✅ **Извлечение чата с opendemo.ru** в форматах TXT, JSON или HTML
- ✅ Автоматическое определение формата потока (HLS/M3U8)
- ✅ Выбор наилучшего качества из доступных
- ✅ Параллельное скачивание сегментов (по умолчанию 5 потоков)
- ✅ Отображение прогресса скачивания
- ✅ Автоматическое объединение сегментов в единый файл
- ✅ Повторные попытки при ошибках сети (до 3 раз)
- ✅ Обработка конфликтов имен файлов

## Установка

### Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Установка зависимостей

**Базовые зависимости (для скачивания видео):**
```bash
pip install -r requirements.txt
```

**Для извлечения чата (опционально):**
```bash
pip install selenium
```

### Установка пакета

```bash
pip install -e .
```

После установки команда `facecast-dl` будет доступна глобально.

## Быстрый старт

### Скачивание видео

**Facecast.net:**
```bash
python -m src.download https://facecast.net/w/311ty3
```

**Opendemo.ru:**
```bash
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1"
```

**Важно:** На Windows используйте кавычки для URL с символом `&`

### Извлечение чата

```bash
python download_chat.py zfvfh8 1
```

Создаст 3 файла: `zfvfh8_chat.txt`, `zfvfh8_chat.json`, `zfvfh8_chat.html`

## Использование

### Скачивание видео

#### Параметры командной строки

- `-o, --output-dir` - директория для сохранения (по умолчанию: текущая)
- `-f, --filename` - имя файла (по умолчанию: video_id.mp4)
- `-w, --workers` - количество параллельных потоков (по умолчанию: 5)
- `-h, --help` - показать справку

#### Примеры

**С указанием директории:**
```bash
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos
```

**С указанием имени файла:**
```bash
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -f presentation.mp4
```

**С увеличенным количеством потоков (быстрее):**
```bash
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -w 10
```

**Все параметры вместе:**
```bash
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos -f video.mp4 -w 10
```

**Использование установленного пакета:**
```bash
facecast-dl "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos
```

#### Рекомендации по количеству потоков

- **Для быстрого скачивания**: 10-15 потоков (`-w 10`)
- **Для медленного интернета**: 3-5 потоков (по умолчанию 5)
- **Не используйте более 20 потоков** - может привести к блокировке

### Извлечение чата с Opendemo.ru

Чат извлекается с помощью браузерной автоматизации (Selenium), так как он загружается динамически через JavaScript.

#### Требования

```bash
pip install selenium
```

Также требуется установленный Chrome/Chromium браузер.

#### Командная строка

```bash
python download_chat.py <video_id> <code>
```

**Примеры:**
```bash
# Базовое использование
python download_chat.py zfvfh8 1

# Справка
python download_chat.py --help
```

**Результат:**
Создаст 3 файла:
- `<video_id>_chat.txt` - текстовый формат для чтения
- `<video_id>_chat.json` - JSON для программной обработки
- `<video_id>_chat.html` - HTML для просмотра в браузере

#### Программное использование

```python
from src.opendemo_chat import OpendemoChat

# Создаем экстрактор
extractor = OpendemoChat(headless=True)

# Извлекаем чат
messages = extractor.extract_chat('zfvfh8', code='1', wait_time=15)

# Сохраняем в разных форматах
extractor.save_txt(messages, 'chat.txt')
extractor.save_json(messages, 'chat.json')
extractor.save_html(messages, 'chat.html')

# Обработка сообщений
for msg in messages:
    print(f"[{msg['time']}] {msg['author']}: {msg['text']}")
```

#### Параметры

- `video_id` (str) - ID видео с opendemo.ru
- `code` (str, optional) - код доступа к видео
- `wait_time` (int) - время ожидания загрузки сообщений в секундах (по умолчанию 15)
- `headless` (bool) - запускать браузер в фоновом режиме (по умолчанию True)

#### Форматы сохранения

**TXT формат:**
```
================================================================================
Чат с opendemo.ru
Сохранено: 2025-11-26 21:33:07
Всего сообщений: 120
================================================================================

[15:00] Антон Середкин (Базис):
Привет, коллеги! Доброе утро!

[16:05] Леонтьев Дмитрий (Рубитех):
Коллеги, добрый день!
```

**JSON формат:**
```json
{
  "saved_at": "2025-11-26T21:33:07",
  "message_count": 120,
  "messages": [
    {
      "time": "15:00",
      "author": "Антон Середкин (Базис)",
      "text": "Привет, коллеги! Доброе утро!"
    }
  ]
}
```

**HTML формат:**
Красиво оформленная веб-страница для просмотра в браузере.

#### Как работает извлечение чата

1. **Загрузка страницы** - Selenium открывает страницу opendemo.ru
2. **Поиск iframe** - Находит iframe с facecast.net, где размещено видео
3. **Переключение на iframe** - Переключается в контекст iframe
4. **Ожидание чата** - Ждет загрузки виджета HyperComments
5. **Извлечение** - Использует JavaScript для извлечения всех сообщений
6. **Парсинг** - Обрабатывает сырые данные и структурирует их
7. **Сохранение** - Сохраняет в выбранных форматах

#### Особенности

- Чат загружается динамически через JavaScript
- Требуется браузерная автоматизация (Selenium)
- Процесс занимает 15-30 секунд
- Виджет HyperComments загружается внутри iframe
- Не доступен через REST API

#### Устранение неполадок

**Selenium не установлен:**
```
✗ Selenium не установлен!
```
Решение: `pip install selenium`

**Chrome не найден:**
```
selenium.common.exceptions.WebDriverException
```
Решение: Убедитесь, что Chrome установлен

**Чат не загружается:**
```
⚠ Чат не найден или пуст
```
Возможные причины:
- Чат отключен для этого видео
- Неправильный код доступа
- Недостаточно времени ожидания

Решение: Увеличьте `wait_time`:
```python
messages = extractor.extract_chat('zfvfh8', code='1', wait_time=30)
```

## Как это работает

### Скачивание видео

1. **Парсинг URL** - извлекается video_id и опциональный код доступа
   - Для facecast.net: `https://facecast.net/w/{video_id}`
   - Для opendemo.ru: `https://opendemo.ru/live?id={video_id}&code={access_code}`
2. **Получение метаданных** - загружается HTML-страница и извлекаются данные о видео
3. **Построение URL потока** - формируется URL для M3U8 плейлиста
4. **Парсинг M3U8** - извлекаются URL всех видео сегментов
5. **Параллельное скачивание** - сегменты скачиваются одновременно в несколько потоков
6. **Объединение** - все сегменты объединяются в единый MP4 файл

### Интеграция с Opendemo.ru

Opendemo.ru использует встроенный iframe с facecast.net для отображения видео. Инструмент автоматически:
- Извлекает `id` и `code` из URL opendemo.ru
- Преобразует их в соответствующий URL facecast.net с параметром `key`
- Скачивает видео напрямую с серверов facecast.net

## Примеры использования

### Скачивание с Facecast.net

```bash
# Базовое использование
python -m src.download https://facecast.net/w/311ty3

# С указанием директории
python -m src.download https://facecast.net/w/311ty3 -o ./downloads

# С указанием имени файла
python -m src.download https://facecast.net/w/311ty3 -f my_video.mp4

# С увеличенным количеством потоков
python -m src.download https://facecast.net/w/311ty3 -w 10
```

### Скачивание с Opendemo.ru

```bash
# Базовое использование (с кодом доступа)
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1"

# С указанием директории
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos

# С указанием имени файла
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -f presentation.mp4

# С увеличенным количеством потоков
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -w 15

# Все параметры вместе
python -m src.download "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos -f video.mp4 -w 10
```

### Извлечение чата

```bash
# Базовое использование
python download_chat.py zfvfh8 1

# Справка
python download_chat.py --help
```

### Использование установленного пакета

```bash
facecast-dl https://facecast.net/w/311ty3
facecast-dl "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos
```

## Структура проекта

```
facecast-downloader/
├── src/
│   ├── __init__.py
│   ├── download.py         # CLI интерфейс для скачивания видео
│   ├── url_parser.py       # Парсинг URL
│   ├── metadata.py         # Извлечение метаданных видео
│   ├── m3u8_parser.py      # Парсинг M3U8 плейлистов
│   ├── downloader.py       # Скачивание сегментов
│   ├── progress.py         # Отображение прогресса
│   ├── file_manager.py     # Управление файлами
│   └── opendemo_chat.py    # Извлечение чата с opendemo.ru
├── download_chat.py        # CLI для извлечения чата
├── tests/                  # Тесты
├── requirements.txt        # Зависимости
├── setup.py               # Установка пакета
└── README.md              # Документация
```

## Зависимости

### Основные (для скачивания видео)
- **requests** - HTTP-запросы
- **beautifulsoup4** - Парсинг HTML

### Для извлечения чата (опционально)
- **selenium** - Браузерная автоматизация

### Разработка
- **pytest** - Тестирование
- **hypothesis** - Property-based тестирование

## Производительность

Параллельное скачивание значительно ускоряет процесс:

- **1 поток**: ~100% времени (базовая линия)
- **5 потоков** (по умолчанию): ~20-30% времени
- **10 потоков**: ~15-20% времени
- **20+ потоков**: может привести к ограничениям со стороны сервера

Рекомендуется использовать 5-10 потоков для оптимального баланса между скоростью и нагрузкой на сервер.

## Обработка ошибок

Программа автоматически обрабатывает:

- ✅ Сетевые ошибки (повторные попытки)
- ✅ Невалидные URL
- ✅ Недоступные видео
- ✅ Ошибки файловой системы
- ✅ Конфликты имен файлов

## Ограничения

- Поддерживаются только видео с facecast.net и opendemo.ru
- Для opendemo.ru поддерживаются видео с кодом доступа
- Скачиваются только завершенные трансляции (не live)
- Извлечение чата требует Selenium и Chrome
- Парсинг чата не идеален (могут быть дубликаты)

## Разработка

### Запуск тестов

```bash
pytest tests/
```

### Property-based тесты

```bash
pytest tests/test_properties.py
```

## Лицензия

MIT License

## Автор

Создано с помощью Kiro AI
