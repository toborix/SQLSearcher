import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union


class SqlSearcher:
    """
    Класс для управления SQL-скриптами.
    Позволяет хранить, искать и получать SQL-скрипты.
    """

    def __init__(self, metadata_file: str = "scripts_metadata.json", scripts_dir: str = "."):
        """
        Инициализация SqlSearcher.
        
        Args:
            metadata_file: Путь к файлу с метаданными скриптов.
            scripts_dir: Базовая директория для хранения скриптов.
        """
        self.metadata_file = metadata_file
        self.scripts_dir = Path(scripts_dir)
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Загружает метаданные из файла или создает пустой словарь."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Ошибка при чтении файла метаданных {self.metadata_file}. Создаю новый.")
                return {"scripts": []}
        return {"scripts": []}
    
    def _save_metadata(self) -> None:
        """Сохраняет метаданные в файл."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def add_script(self, name: str, category: str, description: str, 
                  script_content: str = None, script_path: str = None) -> bool:
        """
        Добавляет новый SQL-скрипт.
        
        Args:
            name: Название скрипта.
            category: Категория скрипта.
            description: Описание скрипта.
            script_content: Содержимое SQL-скрипта (если передается напрямую).
            script_path: Путь к файлу скрипта (если скрипт уже существует).
            
        Returns:
            bool: True, если скрипт успешно добавлен, иначе False.
        """
        # Проверка на дубликаты
        if self._script_exists(name):
            print(f"Скрипт с названием '{name}' уже существует.")
            return False
        
        # Создание директории категории, если она не существует
        category_dir = self.scripts_dir / category
        if not category_dir.exists():
            category_dir.mkdir(parents=True, exist_ok=True)
        
        # Определение пути к файлу скрипта
        if script_path:
            file_path = Path(script_path)
        else:
            # Создаем имя файла из названия скрипта (заменяем пробелы на подчеркивания)
            file_name = f"{name.replace(' ', '_').lower()}.sql"
            file_path = category_dir / file_name
        
        # Запись содержимого скрипта в файл, если оно предоставлено
        if script_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
        elif not file_path.exists():
            print(f"Ошибка: файл {file_path} не существует, а содержимое скрипта не предоставлено.")
            return False
        
        # Добавление метаданных
        script_info = {
            "name": name,
            "category": category,
            "description": description,
            "path": str(file_path),
            "created_at": self._get_current_timestamp(),
            "version": 1
        }
        
        self.metadata["scripts"].append(script_info)
        self._save_metadata()
        
        print(f"Скрипт '{name}' успешно добавлен в категорию '{category}'.")
        return True
    
    def _script_exists(self, name: str) -> bool:
        """Проверяет, существует ли скрипт с указанным названием."""
        return any(script["name"] == name for script in self.metadata["scripts"])
    
    def find_script_by_name(self, name: str) -> Optional[Dict]:
        """
        Ищет скрипт по названию.
        
        Args:
            name: Название скрипта.
            
        Returns:
            Dict или None: Информация о скрипте или None, если скрипт не найден.
        """
        for script in self.metadata["scripts"]:
            if script["name"] == name:
                return self._get_script_with_content(script)
        return None
    
    def find_scripts_by_category(self, category: str) -> List[Dict]:
        """
        Ищет скрипты по категории.
        
        Args:
            category: Категория скриптов.
            
        Returns:
            List[Dict]: Список скриптов в указанной категории.
        """
        scripts = []
        for script in self.metadata["scripts"]:
            if script["category"] == category:
                scripts.append(self._get_script_with_content(script))
        return scripts
    
    def _get_script_with_content(self, script_info: Dict) -> Dict:
        """
        Получает информацию о скрипте вместе с его содержимым.
        
        Args:
            script_info: Метаданные скрипта.
            
        Returns:
            Dict: Метаданные скрипта с добавленным содержимым.
        """
        result = script_info.copy()
        try:
            with open(script_info["path"], 'r', encoding='utf-8') as f:
                result["content"] = f.read()
        except FileNotFoundError:
            result["content"] = f"ОШИБКА: Файл {script_info['path']} не найден."
        return result
    
    def get_all_scripts(self) -> List[Dict]:
        """
        Возвращает список всех скриптов.
        
        Returns:
            List[Dict]: Список всех скриптов.
        """
        return [self._get_script_with_content(script) for script in self.metadata["scripts"]]
    
    def get_all_categories(self) -> List[str]:
        """
        Возвращает список всех категорий.
        
        Returns:
            List[str]: Список всех категорий.
        """
        return list(set(script["category"] for script in self.metadata["scripts"]))
    
    def delete_script(self, name: str, delete_file: bool = False) -> bool:
        """
        Удаляет скрипт из метаданных и опционально удаляет файл.
        
        Args:
            name: Название скрипта.
            delete_file: Если True, то файл скрипта также будет удален.
            
        Returns:
            bool: True, если скрипт успешно удален, иначе False.
        """
        for i, script in enumerate(self.metadata["scripts"]):
            if script["name"] == name:
                if delete_file:
                    try:
                        os.remove(script["path"])
                    except FileNotFoundError:
                        print(f"Предупреждение: файл {script['path']} не найден.")
                
                del self.metadata["scripts"][i]
                self._save_metadata()
                print(f"Скрипт '{name}' успешно удален.")
                return True
        
        print(f"Скрипт с названием '{name}' не найден.")
        return False
    
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
            if query.lower() in script_with_content["content"].lower() or \
               query.lower() in script_with_content["name"].lower() or \
               query.lower() in script_with_content["description"].lower():
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
            print(f"Скрипт с названием '{name}' не найден.")
            return False
            
        # Сохраняем предыдущую версию
        version = script.get("version", 0) + 1
        history_dir = self.scripts_dir / "_history" / name.replace(' ', '_').lower()
        history_dir.mkdir(parents=True, exist_ok=True)
        
        with open(history_dir / f"v{version-1}.sql", "w", encoding='utf-8') as f:
            f.write(script["content"])
            
        # Обновляем скрипт
        with open(script["path"], "w", encoding='utf-8') as f:
            f.write(new_content)
            
        # Обновляем метаданные
        for i, s in enumerate(self.metadata["scripts"]):
            if s["name"] == name:
                self.metadata["scripts"][i]["version"] = version
                self.metadata["scripts"][i]["updated_at"] = self._get_current_timestamp()
                break
                
        self._save_metadata()
        print(f"Скрипт '{name}' успешно обновлен до версии {version}.")
        return True
    
    def get_script_history(self, name: str) -> List[Dict]:
        """
        Получает историю версий скрипта.
        
        Args:
            name: Название скрипта.
            
        Returns:
            List[Dict]: Список версий скрипта.
        """
        script = self.find_script_by_name(name)
        if not script:
            print(f"Скрипт с названием '{name}' не найден.")
            return []
        
        history_dir = self.scripts_dir / "_history" / name.replace(' ', '_').lower()
        if not history_dir.exists():
            print(f"История для скрипта '{name}' не найдена.")
            return []
        
        versions = []
        for version_file in sorted(history_dir.glob("v*.sql")):
            version_num = int(version_file.stem[1:])
            with open(version_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            versions.append({
                "version": version_num,
                "content": content,
                "path": str(version_file)
            })
        
        # Добавляем текущую версию
        versions.append({
            "version": script.get("version", 1),
            "content": script["content"],
            "path": script["path"],
            "current": True
        })
        
        return sorted(versions, key=lambda x: x["version"])
    
    def _get_current_timestamp(self) -> str:
        """Возвращает текущую дату и время в формате ISO."""
        from datetime import datetime
        return datetime.now().isoformat() 