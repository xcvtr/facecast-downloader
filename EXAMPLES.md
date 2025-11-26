# Примеры использования

## Скачивание с Facecast.net

### Базовое использование
```bash
python -m src.cli https://facecast.net/w/311ty3
```

### С указанием директории
```bash
python -m src.cli https://facecast.net/w/311ty3 -o ./downloads
```

### С указанием имени файла
```bash
python -m src.cli https://facecast.net/w/311ty3 -f my_video.mp4
```

### С увеличенным количеством потоков
```bash
python -m src.cli https://facecast.net/w/311ty3 -w 10
```

## Скачивание с Opendemo.ru

### Базовое использование (с кодом доступа)
```bash
python -m src.cli "https://opendemo.ru/live?id=zfvfh8&code=1"
```

**Важно:** На Windows в PowerShell используйте кавычки вокруг URL с символом `&`

### С указанием директории
```bash
python -m src.cli "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos
```

### С указанием имени файла
```bash
python -m src.cli "https://opendemo.ru/live?id=zfvfh8&code=1" -f presentation.mp4
```

### С увеличенным количеством потоков
```bash
python -m src.cli "https://opendemo.ru/live?id=zfvfh8&code=1" -w 15
```

### Все параметры вместе
```bash
python -m src.cli "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos -f video.mp4 -w 10
```

## Скачивание без кода доступа (если видео публичное)
```bash
python -m src.cli "https://opendemo.ru/live?id=abc123"
```

## Использование установленного пакета

После установки через `pip install -e .`:

```bash
facecast-dl https://facecast.net/w/311ty3
facecast-dl "https://opendemo.ru/live?id=zfvfh8&code=1" -o ./videos
```

## Рекомендации

- Для быстрого скачивания используйте 10-15 потоков (`-w 10`)
- Для медленного интернета используйте 3-5 потоков (по умолчанию 5)
- Не используйте более 20 потоков - может привести к блокировке
- На Windows всегда используйте кавычки для URL с символом `&`
