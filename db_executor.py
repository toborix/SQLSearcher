#!/usr/bin/env python3
"""
Модуль для выполнения SQL-скриптов в базах данных.
Поддерживает различные типы баз данных через SQLAlchemy.
"""
import os
import re
from typing import Dict, List, Any, Optional, Union, Tuple
import sqlalchemy
from sqlalchemy import create_engine, text
from sql_searcher import SqlSearcher


class DbExecutor:
    """
    Класс для выполнения SQL-скриптов в базах данных.
    Использует SqlSearcher для поиска скриптов и SQLAlchemy для выполнения.
    """

    def __init__(self, connection_string: str, searcher: Optional[SqlSearcher] = None,
                 metadata_file: str = "scripts_metadata.json", scripts_dir: str = "."):
        """
        Инициализация DbExecutor.
        
        Args:
            connection_string: Строка подключения к базе данных в формате SQLAlchemy.
            searcher: Экземпляр SqlSearcher или None (будет создан новый).
            metadata_file: Путь к файлу с метаданными скриптов (если searcher не указан).
            scripts_dir: Базовая директория для хранения скриптов (если searcher не указан).
        """
        self.connection_string = connection_string
        self.engine = create_engine(connection_string)
        
        if searcher is None:
            self.searcher = SqlSearcher(metadata_file=metadata_file, scripts_dir=scripts_dir)
        else:
            self.searcher = searcher
    
    def execute_script_by_name(self, name: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Выполняет SQL-скрипт по его названию.
        
        Args:
            name: Название скрипта.
            params: Параметры для подстановки в SQL-запрос.
            
        Returns:
            List[Dict]: Результат выполнения запроса (для SELECT-запросов).
            
        Raises:
            ValueError: Если скрипт не найден.
            sqlalchemy.exc.SQLAlchemyError: При ошибке выполнения запроса.
        """
        script = self.searcher.find_script_by_name(name)
        if not script:
            raise ValueError(f"Скрипт с названием '{name}' не найден.")
        
        return self._execute_sql(script["content"], params)
    
    def execute_script_from_category(self, category: str, script_index: int = 0, 
                                    params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Выполняет SQL-скрипт из указанной категории по индексу.
        
        Args:
            category: Категория скриптов.
            script_index: Индекс скрипта в списке (по умолчанию 0 - первый скрипт).
            params: Параметры для подстановки в SQL-запрос.
            
        Returns:
            List[Dict]: Результат выполнения запроса (для SELECT-запросов).
            
        Raises:
            ValueError: Если категория не найдена или индекс вне диапазона.
            sqlalchemy.exc.SQLAlchemyError: При ошибке выполнения запроса.
        """
        scripts = self.searcher.find_scripts_by_category(category)
        if not scripts:
            raise ValueError(f"Скрипты в категории '{category}' не найдены.")
        
        if script_index < 0 or script_index >= len(scripts):
            raise ValueError(f"Индекс скрипта {script_index} вне диапазона [0, {len(scripts) - 1}].")
        
        return self._execute_sql(scripts[script_index]["content"], params)
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Выполняет произвольный SQL-запрос.
        
        Args:
            sql: SQL-запрос.
            params: Параметры для подстановки в SQL-запрос.
            
        Returns:
            List[Dict]: Результат выполнения запроса (для SELECT-запросов).
            
        Raises:
            sqlalchemy.exc.SQLAlchemyError: При ошибке выполнения запроса.
        """
        return self._execute_sql(sql, params)
    
    def _execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Внутренний метод для выполнения SQL-запроса.
        
        Args:
            sql: SQL-запрос.
            params: Параметры для подстановки в SQL-запрос.
            
        Returns:
            List[Dict]: Результат выполнения запроса (для SELECT-запросов).
            
        Raises:
            sqlalchemy.exc.SQLAlchemyError: При ошибке выполнения запроса.
        """
        if params is None:
            params = {}
        
        # Преобразуем SQL-запрос для совместимости с различными форматами параметров
        # Заменяем @param_name и :param_name на :param_name для SQLAlchemy
        sql_normalized = sql
        
        # Заменяем параметры вида @param_name на :param_name
        at_params = re.findall(r'@(\w+)', sql_normalized)
        for param in at_params:
            sql_normalized = sql_normalized.replace(f'@{param}', f':{param}')
        
        # Заменяем параметры вида ? на позиционные параметры :param_0, :param_1, ...
        if '?' in sql_normalized:
            question_marks = sql_normalized.count('?')
            new_params = {}
            
            # Если параметры переданы как словарь, преобразуем их в список
            if isinstance(params, dict):
                params_list = list(params.values())
            else:
                params_list = params if params else []
            
            # Проверяем, что количество параметров совпадает с количеством ?
            if len(params_list) < question_marks:
                raise ValueError(f"Недостаточно параметров: ожидается {question_marks}, получено {len(params_list)}")
            
            # Заменяем ? на :param_0, :param_1, ... и создаем новый словарь параметров
            for i in range(question_marks):
                param_name = f'param_{i}'
                sql_normalized = sql_normalized.replace('?', f':{param_name}', 1)
                new_params[param_name] = params_list[i]
            
            params = new_params
        
        with self.engine.connect() as connection:
            result = connection.execute(text(sql_normalized), params)
            
            # Если запрос возвращает результаты (SELECT)
            if result.returns_rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
            
            # Для запросов без результатов (INSERT, UPDATE, DELETE)
            return []
    
    def get_connection(self) -> sqlalchemy.engine.Connection:
        """
        Возвращает соединение с базой данных.
        
        Returns:
            sqlalchemy.engine.Connection: Соединение с базой данных.
        """
        return self.engine.connect()
    
    def execute_transaction(self, script_names: List[str], 
                           params_list: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Выполняет несколько скриптов в одной транзакции.
        
        Args:
            script_names: Список названий скриптов для выполнения.
            params_list: Список параметров для каждого скрипта.
            
        Returns:
            bool: True, если транзакция успешно выполнена, иначе False.
            
        Raises:
            ValueError: Если какой-либо скрипт не найден.
        """
        if params_list is None:
            params_list = [{}] * len(script_names)
        
        if len(script_names) != len(params_list):
            raise ValueError("Количество скриптов и наборов параметров должно совпадать.")
        
        # Получаем содержимое всех скриптов
        scripts = []
        for name in script_names:
            script = self.searcher.find_script_by_name(name)
            if not script:
                raise ValueError(f"Скрипт с названием '{name}' не найден.")
            scripts.append(script["content"])
        
        # Выполняем транзакцию
        with self.engine.begin() as connection:
            try:
                for i, (sql, params) in enumerate(zip(scripts, params_list)):
                    # Используем тот же метод нормализации SQL, что и в _execute_sql
                    sql_normalized = sql
                    
                    # Заменяем параметры вида @param_name на :param_name
                    at_params = re.findall(r'@(\w+)', sql_normalized)
                    for param in at_params:
                        sql_normalized = sql_normalized.replace(f'@{param}', f':{param}')
                    
                    # Заменяем параметры вида ? на позиционные параметры :param_0, :param_1, ...
                    if '?' in sql_normalized:
                        question_marks = sql_normalized.count('?')
                        new_params = {}
                        
                        # Если параметры переданы как словарь, преобразуем их в список
                        if isinstance(params, dict):
                            params_list_inner = list(params.values())
                        else:
                            params_list_inner = params if params else []
                        
                        # Проверяем, что количество параметров совпадает с количеством ?
                        if len(params_list_inner) < question_marks:
                            raise ValueError(f"Недостаточно параметров для скрипта {i+1}: ожидается {question_marks}, получено {len(params_list_inner)}")
                        
                        # Заменяем ? на :param_0, :param_1, ... и создаем новый словарь параметров
                        for j in range(question_marks):
                            param_name = f'param_{j}'
                            sql_normalized = sql_normalized.replace('?', f':{param_name}', 1)
                            new_params[param_name] = params_list_inner[j]
                        
                        params = new_params
                    
                    connection.execute(text(sql_normalized), params)
                return True
            except Exception as e:
                print(f"Ошибка при выполнении транзакции: {e}")
                # Транзакция будет автоматически отменена при выходе из блока with
                return False 