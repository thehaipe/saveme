import os
import platform
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import yt_dlp

if platform.system() == 'Windows':
    desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
elif platform.system() == 'Darwin':  
    desktop_path = os.path.join(os.environ['HOME'], 'Desktop')
else:  
    desktop_path = os.path.join(os.environ['HOME'], 'Рабочий стол')

SAVE_PATH = os.path.join(desktop_path, 'saves')

os.makedirs(SAVE_PATH, exist_ok=True)

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\rСкачивание: {d['_percent_str']} из {d['_total_bytes_str']} со скоростью {d['_speed_str']}", end='')
    elif d['status'] == 'finished':
        print('\nЗагрузка завершена.')

def download_with_ytdlp(url, quality):
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(SAVE_PATH, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f'Видео с {url} успешно загружено. Создана папка "saves" на Рабочем Столе, видео находится там.')
    except Exception as e:
        print(f'\nyt-dlp не смог загрузить видео с {url}: {e}')
        return False
    return True

def download_with_scraping(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            video_url = video_tag['src']
            video_response = requests.get(video_url, stream=True)
            filename = os.path.join(SAVE_PATH, video_url.split('/')[-1])
            total_size = int(video_response.headers.get('content-length', 0))
            with open(filename, 'wb') as f:
                downloaded_size = 0
                for chunk in video_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        done = int(50 * downloaded_size / total_size)
                        print(f"\rСкачивание: [{'=' * done}{' ' * (50 - done)}] {downloaded_size / (1024 * 1024):.2f} MB из {total_size / (1024 * 1024):.2f} MB", end='')
            print(f'\nВидео с {url} успешно загружено методом скрейпинга. Создана папка "saves" на Рабочем Столе, видео находится там.')
        else:
            print(f'Не удалось найти тег <video> с прямой ссылкой на видео на {url}.')
    except Exception as e:
        print(f'Ошибка при скрейпинге {url}: {e}')

def choose_quality():
    print("Выберите качество видео:")
    print("1. 1080p")
    print("2. 720p")
    print("3. 480p")
    print("4. 360p")
    choice = input("Введите номер желаемого качества: ")
    quality_dict = {
        '1': 1080,
        '2': 720,
        '3': 480,
        '4': 360
    }
    return quality_dict.get(choice, 720)  # По умолчанию 720p

def download_video(url, quality):
    if not download_with_ytdlp(url, quality):
        download_with_scraping(url)

if __name__ == "__main__":
    quality = choose_quality()
    urls = input("Введите ссылки на видео через пробел: ").split()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda url: download_video(url, quality), urls)
