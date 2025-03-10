# SqlSearcher

SqlSearcher - это инструмент для управления SQL-скриптами, который позволяет хранить, искать и выполнять SQL-скрипты в структурированном виде.

## Возможности

- Хранение SQL-скриптов в структурированном виде (по категориям)
- Добавление метаданных к скриптам (название, категория, описание)
- Быстрый поиск скриптов по названию или категории
- Интеграция с Python для автоматизации выполнения скриптов
- Выполнение SQL-скриптов в различных базах данных через SQLAlchemy
- Командный интерфейс (CLI) для удобного взаимодействия

## Установка

```bash
git clone https://github.com/yourusername/SqlSearcher.git
cd SqlSearcher
pip install -r requirements.txt
```

## Использование

### Python API для управления скриптами

```python
from sql_searcher import SqlSearcher

# Инициализация
searcher = SqlSearcher(metadata_file="scripts_metadata.json", scripts_dir="sql_scripts")

# Добавление скрипта
searcher.add_script(
    name="Получить активных пользователей",
    category="selects",
    description="Скрипт для получения списка активных пользователей",
    script_content="SELECT * FROM users WHERE status = 'active';"
)

# Поиск скрипта по названию
script = searcher.find_script_by_name("Получить активных пользователей")
print(script["content"])

# Поиск скриптов по категории
scripts = searcher.find_scripts_by_category("selects")
for script in scripts:
    print(f"{script['name']}: {script['description']}")
```

### Python API для выполнения скриптов в базе данных

```python
from sql_searcher import SqlSearcher
from db_executor import DbExecutor

# Инициализация
searcher = SqlSearcher(metadata_file="scripts_metadata.json", scripts_dir="sql_scripts")
executor = DbExecutor(connection_string="sqlite:///example.db", searcher=searcher)

# Выполнение скрипта по имени
results = executor.execute_script_by_name("Получить активных пользователей")
for row in results:
    print(row)

# Выполнение скрипта с параметрами
results = executor.execute_script_by_name("Получить пользователя по ID", {"user_id": 1})
for row in results:
    print(row)

# Выполнение транзакции
success = executor.execute_transaction(
    ["Обновить статус пользователя", "Получить пользователя по ID"],
    [{"user_id": 1, "new_status": "inactive"}, {"user_id": 1}]
)
```

### Командная строка (CLI)

#### Добавление скрипта

```bash
python cli.py add --name "Получить активных пользователей" --category "selects" --description "Скрипт для получения списка активных пользователей" --content "SELECT * FROM users WHERE status = 'active';"
```

Или из файла:

```bash
python cli.py add --name "Получить активных пользователей" --category "selects" --description "Скрипт для получения списка активных пользователей" --file path/to/script.sql
```

#### Поиск скрипта по названию

```bash
python cli.py find-name "Получить активных пользователей"
```

#### Поиск скриптов по категории

```bash
python cli.py find-category "selects"
```

#### Вывод всех скриптов

```bash
python cli.py list-all
```

#### Вывод всех категорий

```bash
python cli.py list-categories
```

#### Удаление скрипта

```bash
python cli.py delete "Получить активных пользователей"
```

С удалением файла:

```bash
python cli.py delete "Получить активных пользователей" --delete-file
```

## Примеры

В проекте есть несколько примеров использования:

- `example.py` - пример использования SqlSearcher для управления скриптами
- `db_example.py` - пример использования DbExecutor для выполнения скриптов в базе данных

## Структура проекта

- `sql_searcher.py` - основной модуль Python для работы со скриптами
- `db_executor.py` - модуль для выполнения SQL-скриптов в базах данных
- `cli.py` - командный интерфейс
- `scripts_metadata.json` - файл с метаданными скриптов
- `sql_scripts/` - директория для хранения SQL-скриптов по категориям

## Лицензия

MIT 