"""CLI интерфейс для Facecast Video Downloader"""

import sys
import argparse
import requests

from .url_parser import URLParser, URLParseError
from .metadata import VideoMetadataExtractor, MetadataExtractionError
from .m3u8_parser import M3U8Parser, M3U8ParseError
from .downloader import VideoDownloader, DownloadError
from .file_manager import FileManager
from .chat_downloader import ChatDownloader, ChatDownloadError


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description='Скачивание видео с facecast.net и opendemo.ru',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s https://facecast.net/w/311ty3
  %(prog)s https://opendemo.ru/live?id=zfvfh8&code=1
  %(prog)s https://opendemo.ru/live?id=zfvfh8&code=1 -o ./videos
  %(prog)s https://opendemo.ru/live?id=zfvfh8&code=1 -o ./videos -f video.mp4
  %(prog)s https://opendemo.ru/live?id=zfvfh8&code=1 -w 10  # 10 параллельных потоков
        """
    )
    
    parser.add_argument(
        'url',
        help='URL видео на facecast.net или opendemo.ru (например: https://facecast.net/w/311ty3 или https://opendemo.ru/live?id=zfvfh8&code=1)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Директория для сохранения видео (по умолчанию: текущая директория)'
    )
    
    parser.add_argument(
        '-f', '--filename',
        help='Имя выходного файла (по умолчанию: используется video_id)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='Количество параллельных потоков для скачивания (по умолчанию: 5)'
    )
    
    parser.add_argument(
        '--save-chat',
        action='store_true',
        help='Сохранить чат вместе с видео'
    )
    
    parser.add_argument(
        '--chat-format',
        choices=['txt', 'json', 'html', 'all'],
        default='txt',
        help='Формат сохранения чата (по умолчанию: txt)'
    )
    
    parser.add_argument(
        '--chat-only',
        action='store_true',
        help='Скачать только чат без видео (для отладки)'
    )
    
    args = parser.parse_args()
    
    # Запускаем процесс скачивания
    try:
        result = download_video(args.url, args.output_dir, args.filename, args.workers, args.save_chat, args.chat_format, args.chat_only)
        
        if result.success:
            print(f"\n{'='*60}")
            print(f"✓ Скачивание завершено успешно!")
            print(f"Файл сохранен: {result.output_path}")
            print(f"{'='*60}")
            sys.exit(0)
        else:
            print(f"\n{'='*60}")
            print(f"✗ Ошибка: {result.error_message}")
            print(f"{'='*60}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nСкачивание прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ Неожиданная ошибка: {e}")
        print(f"{'='*60}")
        sys.exit(1)


def download_video(url: str, output_dir: str = '.', filename: str = None, workers: int = 5, save_chat: bool = False, chat_format: str = 'txt', chat_only: bool = False):
    """
    Скачивает видео с facecast.net
    
    Args:
        url: URL видео
        output_dir: Директория для сохранения
        filename: Имя файла (опционально)
        workers: Количество параллельных потоков
        save_chat: Сохранить чат
        chat_format: Формат чата
        chat_only: Скачать только чат без видео
        
    Returns:
        DownloadResult
    """
    from .downloader import DownloadResult
    
    print("="*60)
    print("Facecast Video Downloader")
    print("="*60)
    
    # Шаг 1: Парсинг URL
    print("\n[1/5] Парсинг URL...")
    try:
        url_parser = URLParser()
        video_id, code = url_parser.parse(url)
        print(f"✓ Video ID: {video_id}")
        if code:
            print(f"✓ Access Code: {code}")
    except URLParseError as e:
        return DownloadResult(
            success=False,
            output_path=None,
            error_message=str(e)
        )
    
    # Шаг 2: Получение метаданных видео
    extractor = VideoMetadataExtractor()
    
    if chat_only:
        print("\n[2/5] Режим только чата - пропуск получения видеопотока")
        # Получаем только event_id для чата
        event_id = extractor.get_event_id(video_id, code)
        if event_id:
            print(f"✓ Event ID: {event_id}")
        else:
            print(f"⚠ Event ID не найден, используем Video ID: {video_id}")
            event_id = video_id
    else:
        print("\n[2/5] Получение метаданных видео...")
        try:
            video_info = extractor.extract_stream_url(video_id, code)
            print(f"✓ Найден видеопоток: {video_info.stream_type}")
            print(f"  URL: {video_info.stream_url[:80]}...")
        except MetadataExtractionError as e:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message=str(e)
            )
    
    # Шаг 3: Подготовка выходного файла
    if chat_only:
        print("\n[3/5] Режим только чата - пропуск подготовки видеофайла")
        # Создаем путь для чата
        if filename:
            base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            output_path = FileManager.get_absolute_path(f"{output_dir}/{base_name}_chat")
        else:
            output_path = FileManager.get_absolute_path(f"{output_dir}/{video_id}_chat")
        FileManager.ensure_directory(output_dir)
        print(f"✓ Чат будет сохранен: {output_path}.{chat_format}")
    else:
        print("\n[3/5] Подготовка выходного файла...")
        try:
            if filename:
                output_path = FileManager.get_absolute_path(
                    f"{output_dir}/{filename}"
                )
                FileManager.ensure_directory(output_dir)
            else:
                output_path = FileManager.generate_output_path(
                    video_id, output_dir, "mp4"
                )
            print(f"✓ Файл будет сохранен: {output_path}")
        except Exception as e:
            return DownloadResult(
                success=False,
                output_path=None,
                error_message=f"Ошибка подготовки файла: {e}"
            )
    
    # Шаг 4: Обработка видеопотока
    if chat_only:
        print("\n[4/5] Режим только чата - пропуск")
        print("\n[5/5] Режим только чата - пропуск")
        # Создаем фиктивный результат для продолжения к скачиванию чата
        result = DownloadResult(success=True, output_path=output_path, error_message=None)
    else:
        downloader = VideoDownloader(max_workers=workers)
    
        if video_info.stream_type == 'm3u8':
            print("\n[4/5] Парсинг M3U8 плейлиста...")
            try:
                # Загружаем M3U8 плейлист
                response = requests.get(video_info.stream_url, timeout=30)
                response.raise_for_status()
                m3u8_content = response.text
                
                parser = M3U8Parser()
                
                # Проверяем, является ли это master playlist
                if parser.is_master_playlist(m3u8_content):
                    print("  Обнаружен master playlist, выбираем лучшее качество...")
                    best_quality_url = parser.select_best_quality(m3u8_content)
                    
                    # Преобразуем в абсолютный URL если нужно
                    from urllib.parse import urljoin
                    best_quality_url = urljoin(video_info.stream_url, best_quality_url)
                    
                    # Загружаем плейлист с лучшим качеством
                    response = requests.get(best_quality_url, timeout=30)
                    response.raise_for_status()
                    m3u8_content = response.text
                    base_url = best_quality_url
                else:
                    base_url = video_info.stream_url
                
                # Парсим сегменты
                segment_urls = parser.parse(m3u8_content, base_url)
                print(f"✓ Найдено сегментов: {len(segment_urls)}")
                
            except M3U8ParseError as e:
                return DownloadResult(
                    success=False,
                    output_path=None,
                    error_message=f"Ошибка парсинга M3U8: {e}"
                )
            except requests.RequestException as e:
                return DownloadResult(
                    success=False,
                    output_path=None,
                    error_message=f"Ошибка загрузки плейлиста: {e}"
                )
            
            # Шаг 5: Скачивание сегментов
            print("\n[5/5] Скачивание видео...")
            result = downloader.download_segments(segment_urls, output_path)
            
        else:
            # Прямая ссылка
            print("\n[4/5] Пропуск (прямая ссылка)")
            print("\n[5/5] Скачивание видео...")
            result = downloader.download_direct(video_info.stream_url, output_path)
    
    # Шаг 6: Сохранение чата (если запрошено или chat_only режим)
    if (save_chat or chat_only) and result.success:
        print("\n[6/6] Сохранение чата...")
        try:
            chat_downloader = ChatDownloader()
            # Получаем event_id из extractor или через API
            event_id = extractor.event_id if hasattr(extractor, 'event_id') and extractor.event_id else extractor.get_event_id(video_id, code)
            
            if event_id:
                print(f"  Event ID: {event_id}")
                messages = chat_downloader.download_chat(event_id, code)
            else:
                print("  ⚠ Не удалось получить Event ID, пробуем с Video ID...")
                messages = chat_downloader.download_chat(video_id, code)
            
            if messages:
                import os
                base_name = os.path.splitext(output_path)[0]
                
                if chat_format == 'all':
                    formats = ['txt', 'json', 'html']
                else:
                    formats = [chat_format]
                
                for fmt in formats:
                    chat_path = f"{base_name}_chat.{fmt}"
                    if fmt == 'txt':
                        chat_downloader.save_chat_txt(messages, chat_path)
                    elif fmt == 'json':
                        chat_downloader.save_chat_json(messages, chat_path)
                    elif fmt == 'html':
                        chat_downloader.save_chat_html(messages, chat_path)
                    print(f"✓ Чат сохранен: {chat_path} ({len(messages)} сообщений)")
            else:
                print("⚠ Чат недоступен или пуст")
                print("  Возможные причины:")
                print("  - Чат был отключен во время трансляции")
                print("  - История чата не сохраняется на сервере")
                print("  - Видео слишком старое")
        except Exception as e:
            print(f"⚠ Не удалось сохранить чат: {e}")
    
    return result


if __name__ == '__main__':
    main()
