#!/usr/bin/env python3
import argparse
import sys
from sql_searcher import SqlSearcher


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


def print_script_info(script, include_content=True):
    """Выводит информацию о скрипте в консоль."""
    print(f"Название: {script['name']}")
    print(f"Категория: {script['category']}")
    print(f"Описание: {script['description']}")
    print(f"Путь: {script['path']}")
    
    if include_content:
        print("\nСодержимое:")
        print("-" * 50)
        print(script['content'])


if __name__ == "__main__":
    main() 