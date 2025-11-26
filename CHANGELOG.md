# Changelog

## [Unreleased]

### Added
- Поддержка скачивания видео с opendemo.ru
- Поддержка защищенных видео с кодом доступа (параметр `code`)
- Автоматическое преобразование URL opendemo.ru в facecast.net
- Новый файл EXAMPLES.md с подробными примерами использования

### Changed
- URLParser теперь возвращает tuple (video_id, code) вместо просто video_id
- VideoMetadataExtractor.extract_stream_url() принимает опциональный параметр code
- Обновлена документация в README.md
- Обновлены примеры использования в CLI help

### Technical Details
- Добавлен паттерн OPENDEMO_PATTERN для парсинга URL opendemo.ru
- Параметр code передается как query parameter `key` в URL facecast.net
- Поддержка URL формата: `https://opendemo.ru/live?id={video_id}&code={access_code}`

## [1.0.0] - Initial Release

### Added
- Скачивание видео с facecast.net
- Параллельное скачивание сегментов
- Поддержка M3U8 плейлистов
- Автоматический выбор лучшего качества
- Прогресс-бар для отслеживания скачивания
- Повторные попытки при ошибках сети
