import psycopg2
import asyncio
import psutil

def get_metrics():
    result_str = ''
    try:
        connection = psycopg2.connect(
            user="q_admin",
            password="isvhX4#09",
            host="127.0.0.1",
            port="5432",
            database="q_data"
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        # print("Проверка доступности базы данных: База данных доступна" if result else "Проверка доступности базы данных: Ошибка доступа")
        result_str += "Проверка доступности базы данных: База данных доступна\n" if result else "Проверка доступности базы данных: Ошибка доступа\n"

        cursor.execute("SELECT count(*) FROM pg_stat_activity")
        active_connections = cursor.fetchone()[0]
        # print(f"Количество активных подключений: {active_connections}")
        result_str += f"Количество активных подключений: {active_connections}\n"

        cursor.execute("SELECT pid, wait_event_type, wait_event FROM pg_stat_activity WHERE wait_event_type = 'LWLock';")
        lwlock_events = cursor.fetchone()
        result_str += f"Количество значений LWLock: {len(lwlock_events) if lwlock_events else 0}\n"
        # print(len(lwlock_events) if lwlock_events else 0)
        if connection:
            cursor.close()
            connection.close()
        disk_usage = psutil.disk_usage('/')
        result_str += f"Свободное место на диске (в байтах): {disk_usage.free}\n"
        cpu_percent = psutil.cpu_percent(interval=1)
        result_str += f"Загруженность процессора (%): {cpu_percent}\n"
        # print("Загруженность процессора (%):", cpu_percent)
        # print("Свободное место на диске (в байтах):", disk_usage.free)

    except Exception as e:
        # print("Ошибка при подключении к базе данных PostgreSQL", error)
        result_str = "Ошибка при подключении к базе данных PostgreSQL\n"
        result_str += str(e)

    return result_str

if __name__ == '__main__':
    print(get_metrics())