#!/usr/bin/env python3
import argparse
import sys
from sql_searcher import SqlSearcher
from typing import List, Dict
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Управление SQL-скриптами")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда добавления скрипта
    add_parser = subparsers.add_parser("add", help="Добавить новый SQL-скрипт")
    add_parser.add_argument("--name", "-n", required=True, help="Название скрипта")
    add_parser.add_argument("--category", "-c", required=True, help="Категория скрипта")
    add_parser.add_argument("--description", "-d", required=True, help="Описание скрипта")
    add_parser.add_argument("--content", help="Содержимое SQL-скрипта")
    add_parser.add_argument("--file", "-f", help="Путь к файлу SQL-скрипта")
    
    # Команда поиска скрипта по имени
    find_name_parser = subparsers.add_parser("find-name", help="Найти скрипт по имени")
    find_name_parser.add_argument("name", help="Название скрипта")
    
    # Команда поиска скриптов по категории
    find_category_parser = subparsers.add_parser("find-category", help="Найти скрипты по категории")
    find_category_parser.add_argument("category", help="Категория скриптов")
    
    # Команда вывода всех скриптов
    subparsers.add_parser("list-all", help="Вывести все скрипты")
    
    # Команда вывода всех категорий
    subparsers.add_parser("list-categories", help="Вывести все категории")
    
    # Команда удаления скрипта
    delete_parser = subparsers.add_parser("delete", help="Удалить скрипт")
    delete_parser.add_argument("name", help="Название скрипта")
    delete_parser.add_argument("--delete-file", "-df", action="store_true", 
                              help="Удалить также файл скрипта")
    
    # Команда полнотекстового поиска
    search_parser = subparsers.add_parser("search", help="Полнотекстовый поиск по скриптам")
    search_parser.add_argument("query", help="Поисковый запрос")
    
    # Команда обновления скрипта
    update_parser = subparsers.add_parser("update", help="Обновить содержимое скрипта")
    update_parser.add_argument("name", help="Название скрипта")
    update_parser.add_argument("--content", help="Новое содержимое SQL-скрипта")
    update_parser.add_argument("--file", "-f", help="Путь к файлу с новым содержимым")
    
    # Команда просмотра истории версий скрипта
    history_parser = subparsers.add_parser("history", help="Просмотр истории версий скрипта")
    history_parser.add_argument("name", help="Название скрипта")
    history_parser.add_argument("--version", "-v", type=int, help="Номер версии для просмотра")
    
    # Общие параметры
    parser.add_argument("--metadata-file", default="scripts_metadata.json", 
                       help="Путь к файлу метаданных")
    parser.add_argument("--scripts-dir", default=".", 
                       help="Базовая директория для хранения скриптов")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    searcher = SqlSearcher(metadata_file=args.metadata_file, scripts_dir=args.scripts_dir)
    
    if args.command == "add":
        if not args.content and not args.file:
            print("Ошибка: необходимо указать либо содержимое скрипта (--content), либо путь к файлу (--file)")
            return
        
        content = None
        if args.content:
            content = args.content
        elif args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                print(f"Ошибка: файл {args.file} не найден")
                return
        
        success = searcher.add_script(
            name=args.name,
            category=args.category,
            description=args.description,
            script_content=content
        )
        
        if not success:
            sys.exit(1)
    
    elif args.command == "find-name":
        script = searcher.find_script_by_name(args.name)
        if script:
            print_script_info(script)
        else:
            print(f"Скрипт с названием '{args.name}' не найден.")
            sys.exit(1)
    
    elif args.command == "find-category":
        scripts = searcher.find_scripts_by_category(args.category)
        if scripts:
            for script in scripts:
                print_script_info(script)
                print("-" * 50)
        else:
            print(f"Скрипты в категории '{args.category}' не найдены.")
            sys.exit(1)
    
    elif args.command == "list-all":
        scripts = searcher.get_all_scripts()
        if scripts:
            for script in scripts:
                print_script_info(script, include_content=False)
                print("-" * 50)
        else:
            print("Скрипты не найдены.")
    
    elif args.command == "list-categories":
        categories = searcher.get_all_categories()
        if categories:
            print("Доступные категории:")
            for category in categories:
                print(f"- {category}")
        else:
            print("Категории не найдены.")
    
    elif args.command == "delete":
        success = searcher.delete_script(args.name, delete_file=args.delete_file)
        if not success:
            sys.exit(1)
    
    elif args.command == "search":
        scripts = searcher.search_in_scripts(args.query)
        if scripts:
            print(f"Найдено скриптов: {len(scripts)}")
            for script in scripts:
                print_script_info(script, include_content=False)
                print("-" * 50)
        else:
            print(f"Скрипты, содержащие '{args.query}', не найдены.")
            sys.exit(1)
    
    elif args.command == "update":
        if not args.content and not args.file:
            print("Ошибка: необходимо указать либо новое содержимое скрипта (--content), либо путь к файлу (--file)")
            return
        
        content = None
        if args.content:
            content = args.content
        elif args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                print(f"Ошибка: файл {args.file} не найден")
                return
        
        success = searcher.update_script(args.name, content)
        if not success:
            sys.exit(1)
    
    elif args.command == "history":
        versions = searcher.get_script_history(args.name)
        if not versions:
            sys.exit(1)
        
        if args.version:
            # Вывод конкретной версии
            version_info = next((v for v in versions if v["version"] == args.version), None)
            if version_info:
                print(f"Версия {args.version} скрипта '{args.name}':")
                print("-" * 50)
                print(version_info["content"])
            else:
                print(f"Версия {args.version} скрипта '{args.name}' не найдена.")
                sys.exit(1)
        else:
            # Вывод списка всех версий
            print(f"История версий скрипта '{args.name}':")
            for version in versions:
                current = version.get("current", False)
                print(f"- Версия {version['version']}{' (текущая)' if current else ''}")


def print_script_info(script, include_content=True):
    """Выводит информацию о скрипте в консоль."""
    print(f"Название: {script['name']}")
    print(f"Категория: {script['category']}")
    print(f"Описание: {script['description']}")
    print(f"Путь: {script['path']}")
    
    if "version" in script:
        print(f"Версия: {script['version']}")
    
    if "created_at" in script:
        print(f"Создан: {script['created_at']}")
    
    if "updated_at" in script:
        print(f"Обновлен: {script['updated_at']}")
    
    if include_content:
        print("\nСодержимое:")
        print("-" * 50)
        print(script['content'])


def search_in_scripts(self, query: str) -> List[Dict]:
    """
    Полнотекстовый поиск по содержимому скриптов.
    
    Args:
        query: Поисковый запрос.
        
    Returns:
        List[Dict]: Список скриптов, содержащих запрос.
    """
    results = []
    for script in self.metadata["scripts"]:
        script_with_content = self._get_script_with_content(script)
        if query.lower() in script_with_content["content"].lower():
            results.append(script_with_content)
    return results


def update_script(self, name: str, new_content: str) -> bool:
    """
    Обновляет содержимое скрипта, сохраняя предыдущую версию.
    
    Args:
        name: Название скрипта.
        new_content: Новое содержимое скрипта.
        
    Returns:
        bool: True, если скрипт успешно обновлен, иначе False.
    """
    script = self.find_script_by_name(name)
    if not script:
        return False
        
    # Сохраняем предыдущую версию
    version = script.get("version", 0) + 1
    history_dir = Path(self.scripts_dir) / "_history" / name
    history_dir.mkdir(parents=True, exist_ok=True)
    
    with open(history_dir / f"v{version-1}.sql", "w", encoding="utf-8") as f:
        f.write(script["content"])
        
    # Обновляем скрипт
    with open(script["path"], "w", encoding="utf-8") as f:
        f.write(new_content)
        
    # Обновляем метаданные
    for i, s in enumerate(self.metadata["scripts"]):
        if s["name"] == name:
            self.metadata["scripts"][i]["version"] = version
            self.metadata["scripts"][i]["updated_at"] = datetime.now().isoformat()
            break
            
    self._save_metadata()
    return True


if __name__ == "__main__":
    main() 