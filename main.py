import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sqlite3
import os.path

# Путь к файлу базы данных Firefox
firefox_path = '/home/irina/snap/firefox/common/.mozilla/firefox/67ev7eav.default-1678991437348'
places_db_path =  os.path.join(firefox_path, 'places.sqlite')  # Путь к базе данных адресов
# print(places_db_path)

visited_domains = {} # Словарь уникальных адресов и их количества посещений
n = 5 # Проверка адресов каждые 5 секунд

# Функция создания соединения с базой данных firefox
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

# Функция получения посещенных DNS-доменов
def get_visited_domains(conn):
    global visited_domains
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM moz_places")
        rows = cursor.fetchall()
        for row in rows:
            domain = row[0].split('/')[2]
            if not domain.startswith('localhost'):
                visited_domains[domain] = visited_domains.get(domain, 0) + 1
    except sqlite3.Error as e:
        print(e)

# Класс для отслеживания изменений в файле базы данных
class FileModifiedHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == places_db_path:
            # Файл базы данных изменен
            conn = create_connection(places_db_path)
            if conn is not None:
                get_visited_domains(conn)
                conn.close()

            # Фича
            cat_count = visited_domains.get('www.youtubekids.com', 0)
            if cat_count != 0 and cat_count % 10 == 8:
                # Для www.youtubekids.com проверяем счетчик, если последняя цифра 8, выводим сообщение в консоль
                print(r"    )\_/(")
                print(r"    'o.o'")
                print(r"  =(_ _)=")
                print(r"     U")

# Функция для записи статистики в файл
def write_statistics():
    global visited_domains
    with open("visited_domains.txt", "w") as file:
        for domain, count in visited_domains.items():
            file.write(f"{{ {domain}: {count} }}\n")

# Основная функция для мониторинга активности в реальном времени
def monitor_activity_realtime():
    event_handler = FileModifiedHandler()
    observer = Observer()
    observer.schedule(event_handler, path=firefox_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(n)  # Проверяем каждые n секунд
            write_statistics()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Вызываем функцию мониторинга активности в реальном времени
monitor_activity_realtime()
