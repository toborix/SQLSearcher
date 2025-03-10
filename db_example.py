#!/usr/bin/env python3
"""
Пример использования DbExecutor для выполнения SQL-скриптов.
"""
import os
import sqlite3
from sql_searcher import SqlSearcher
from db_executor import DbExecutor


def main():
    # Создаем тестовую базу данных SQLite
    db_path = "example.db"
    create_test_database(db_path)
    
    # Создаем директорию для скриптов, если она не существует
    os.makedirs("sql_scripts", exist_ok=True)
    
    # Инициализируем SqlSearcher
    searcher = SqlSearcher(metadata_file="scripts_metadata.json", scripts_dir="sql_scripts")
    
    # Добавляем тестовые скрипты
    add_test_scripts(searcher)
    
    # Инициализируем DbExecutor
    executor = DbExecutor(f"sqlite:///{db_path}", searcher=searcher)
    
    # Выполняем скрипт по имени
    print("\n=== Выполнение скрипта 'Получить всех пользователей' ===")
    results = executor.execute_script_by_name("Получить всех пользователей")
    print_results(results)
    
    # Выполняем скрипт с параметрами
    print("\n=== Выполнение скрипта 'Получить пользователя по ID' ===")
    results = executor.execute_script_by_name("Получить пользователя по ID", {"user_id": 2})
    print_results(results)
    
    # Выполняем скрипт из категории
    print("\n=== Выполнение скрипта из категории 'selects' ===")
    results = executor.execute_script_from_category("selects", 0)
    print_results(results)
    
    # Выполняем произвольный SQL-запрос
    print("\n=== Выполнение произвольного SQL-запроса ===")
    results = executor.execute_sql("SELECT * FROM users WHERE status = ?", {"status": "inactive"})
    print_results(results)
    
    # Выполняем транзакцию
    print("\n=== Выполнение транзакции ===")
    success = executor.execute_transaction(
        ["Обновить статус пользователя", "Получить пользователя по ID"],
        [{"user_id": 1, "new_status": "inactive"}, {"user_id": 1}]
    )
    print(f"Транзакция {'успешно выполнена' if success else 'не выполнена'}")
    
    # Проверяем результат транзакции
    if success:
        results = executor.execute_script_by_name("Получить пользователя по ID", {"user_id": 1})
        print_results(results)


def create_test_database(db_path):
    """Создает тестовую базу данных SQLite."""
    # Удаляем существующую базу данных, если она есть
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Создаем новую базу данных и таблицу пользователей
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Добавляем тестовые данные
    users = [
        (1, "user1", "user1@example.com", "active", "2023-01-01 10:00:00"),
        (2, "user2", "user2@example.com", "active", "2023-01-02 11:00:00"),
        (3, "user3", "user3@example.com", "inactive", "2023-01-03 12:00:00"),
        (4, "user4", "user4@example.com", "active", "2023-01-04 13:00:00"),
        (5, "user5", "user5@example.com", "deleted", "2023-01-05 14:00:00")
    ]
    
    cursor.executemany(
        "INSERT INTO users (id, username, email, status, created_at) VALUES (?, ?, ?, ?, ?)",
        users
    )
    
    conn.commit()
    conn.close()
    
    print(f"Тестовая база данных создана: {db_path}")


def add_test_scripts(searcher):
    """Добавляет тестовые SQL-скрипты в SqlSearcher."""
    # Проверяем, существуют ли уже скрипты
    if searcher.find_script_by_name("Получить всех пользователей"):
        print("Тестовые скрипты уже добавлены.")
        return
    
    print("Добавление тестовых скриптов...")
    
    # Скрипт для получения всех пользователей
    searcher.add_script(
        name="Получить всех пользователей",
        category="selects",
        description="Получает список всех пользователей",
        script_content="SELECT * FROM users"
    )
    
    # Скрипт для получения пользователя по ID
    searcher.add_script(
        name="Получить пользователя по ID",
        category="selects",
        description="Получает пользователя по его ID",
        script_content="SELECT * FROM users WHERE id = :user_id"
    )
    
    # Скрипт для получения активных пользователей
    searcher.add_script(
        name="Получить активных пользователей",
        category="selects",
        description="Получает список активных пользователей",
        script_content="SELECT * FROM users WHERE status = 'active'"
    )
    
    # Скрипт для обновления статуса пользователя
    searcher.add_script(
        name="Обновить статус пользователя",
        category="updates",
        description="Обновляет статус пользователя",
        script_content="UPDATE users SET status = :new_status WHERE id = :user_id"
    )
    
    print("Тестовые скрипты успешно добавлены.")


def print_results(results):
    """Выводит результаты выполнения SQL-запроса."""
    if not results:
        print("Запрос не вернул результатов.")
        return
    
    # Выводим заголовки столбцов
    columns = results[0].keys()
    header = " | ".join(columns)
    print(header)
    print("-" * len(header))
    
    # Выводим данные
    for row in results:
        print(" | ".join(str(row[col]) for col in columns))


if __name__ == "__main__":
    main() 