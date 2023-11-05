import psycopg2
import psutil

def get_metrics(user, password, database):
    result = {
            'type':'ok',
            'data': {
                'connections': 0, 
                'LWLock': 0,
                'disk_space': 0,
                'cpu': 0
                }
            }
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host="127.0.0.1",
            port="5432",
            database=database
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT count(*) FROM pg_stat_activity")
        active_connections = cursor.fetchone()[0]
        # print(f"Количество активных подключений: {active_connections}")
        # result_str += f"Количество активных подключений: {active_connections}\n"
        result['data']['connections'] = active_connections

        cursor.execute("SELECT pid, wait_event_type, wait_event FROM pg_stat_activity WHERE wait_event_type = 'LWLock';")
        lwlock_events = cursor.fetchone()
        # result_str += f"Количество значений LWLock: {len(lwlock_events) if lwlock_events else 0}\n"
        result['data']['LWLock'] = lwlock_events
        # print(len(lwlock_events) if lwlock_events else 0)
        if connection:
            cursor.close()
            connection.close()
        disk_usage = psutil.disk_usage('/')
        # result_str += f"Свободное место на диске (в байтах): {disk_usage.free}\n"
        result['data']['disk_space'] = disk_usage.free
        cpu_percent = psutil.cpu_percent(interval=1)
        # result_str += f"Загруженность процессора (%): {cpu_percent}\n"
        result['data']['cpu'] = cpu_percent
        # print("Загруженность процессора (%):", cpu_percent)
        # print("Свободное место на диске (в байтах):", disk_usage.free)

    except Exception as e:
        # print("Ошибка при подключении к базе данных PostgreSQL", error)
        # result_str = "Ошибка при подключении к базе данных PostgreSQL\n"
        # result_str += str(e)
        result = {
                'type': 'error',
                'data': {
                    'error': str(e)
                    }
                }

    return result

if __name__ == '__main__':
    print(get_metrics())
