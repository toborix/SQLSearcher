#!/usr/bin/env python3
"""
Пример использования SqlSearcher для управления SQL-скриптами.
"""
import os
from sql_searcher import SqlSearcher


def main():
    # Создаем директорию для скриптов, если она не существует
    os.makedirs("sql_scripts", exist_ok=True)
    
    # Инициализируем SqlSearcher
    searcher = SqlSearcher(metadata_file="scripts_metadata.json", scripts_dir="sql_scripts")
    
    # Добавляем скрипты из примеров
    add_example_scripts(searcher)
    
    # Демонстрация поиска скриптов
    print("\n=== Поиск скрипта по названию ===")
    script = searcher.find_script_by_name("Получить активных пользователей")
    if script:
        print(f"Найден скрипт: {script['name']}")
        print(f"Описание: {script['description']}")
        print(f"Путь: {script['path']}")
        print("\nСодержимое:")
        print("-" * 50)
        print(script['content'])
    
    print("\n=== Поиск скриптов по категории ===")
    scripts = searcher.find_scripts_by_category("updates")
    if scripts:
        for script in scripts:
            print(f"Найден скрипт: {script['name']}")
            print(f"Описание: {script['description']}")
            print(f"Путь: {script['path']}")
            print("-" * 50)
    
    print("\n=== Список всех категорий ===")
    categories = searcher.get_all_categories()
    for category in categories:
        print(f"- {category}")
    
    print("\n=== Список всех скриптов ===")
    all_scripts = searcher.get_all_scripts()
    for script in all_scripts:
        print(f"- {script['name']} ({script['category']})")


def add_example_scripts(searcher):
    """Добавляет примеры скриптов в SqlSearcher."""
    # Проверяем, существуют ли уже скрипты
    if searcher.find_script_by_name("Получить активных пользователей"):
        print("Примеры скриптов уже добавлены.")
        return
    
    print("Добавление примеров скриптов...")
    
    # Добавляем скрипт для получения активных пользователей
    with open("examples/selects/get_active_users.sql", "r", encoding="utf-8") as f:
        content = f.read()
    
    searcher.add_script(
        name="Получить активных пользователей",
        category="selects",
        description="Скрипт для получения списка активных пользователей",
        script_content=content
    )
    
    # Добавляем скрипт для обновления статуса пользователя
    with open("examples/updates/update_user_status.sql", "r", encoding="utf-8") as f:
        content = f.read()
    
    searcher.add_script(
        name="Обновить статус пользователя",
        category="updates",
        description="Скрипт для обновления статуса пользователя на 'inactive'",
        script_content=content
    )
    
    # Добавляем еще один скрипт напрямую
    searcher.add_script(
        name="Удалить пользователя",
        category="deletes",
        description="Скрипт для мягкого удаления пользователя",
        script_content="""-- Мягкое удаление пользователя
UPDATE 
    users
SET 
    deleted_at = CURRENT_TIMESTAMP,
    status = 'deleted'
WHERE 
    id = :user_id
    AND deleted_at IS NULL;"""
    )
    
    print("Примеры скриптов успешно добавлены.")


if __name__ == "__main__":
    main() 