#!/usr/bin/env python3
"""
Тесты для класса SqlSearcher.
"""
import unittest
import os
import shutil
import tempfile
from pathlib import Path
from sql_searcher import SqlSearcher


class TestSqlSearcher(unittest.TestCase):
    """Тесты для класса SqlSearcher."""
    
    def setUp(self):
        """Подготовка к тестам."""
        # Создаем временную директорию для тестов
        self.test_dir = tempfile.mkdtemp()
        self.metadata_file = os.path.join(self.test_dir, "test_metadata.json")
        self.scripts_dir = os.path.join(self.test_dir, "test_scripts")
        
        # Создаем экземпляр SqlSearcher
        self.searcher = SqlSearcher(metadata_file=self.metadata_file, scripts_dir=self.scripts_dir)
        
        # Добавляем тестовые скрипты
        self.searcher.add_script(
            name="Test Script 1",
            category="test",
            description="Test description 1",
            script_content="SELECT * FROM test WHERE id = 1"
        )
        
        self.searcher.add_script(
            name="Test Script 2",
            category="test",
            description="Test description 2",
            script_content="SELECT * FROM test WHERE name = 'test'"
        )
        
        self.searcher.add_script(
            name="Another Script",
            category="another",
            description="Another description",
            script_content="UPDATE test SET name = 'updated' WHERE id = 1"
        )
    
    def tearDown(self):
        """Очистка после тестов."""
        # Удаляем временную директорию
        shutil.rmtree(self.test_dir)
    
    def test_add_script(self):
        """Тест добавления скрипта."""
        # Добавляем новый скрипт
        result = self.searcher.add_script(
            name="New Script",
            category="new",
            description="New description",
            script_content="INSERT INTO test VALUES (1, 'test')"
        )
        
        # Проверяем, что скрипт успешно добавлен
        self.assertTrue(result)
        
        # Проверяем, что скрипт можно найти
        script = self.searcher.find_script_by_name("New Script")
        self.assertIsNotNone(script)
        self.assertEqual(script["name"], "New Script")
        self.assertEqual(script["category"], "new")
        self.assertEqual(script["description"], "New description")
        self.assertEqual(script["content"], "INSERT INTO test VALUES (1, 'test')")
    
    def test_find_script_by_name(self):
        """Тест поиска скрипта по имени."""
        # Ищем существующий скрипт
        script = self.searcher.find_script_by_name("Test Script 1")
        self.assertIsNotNone(script)
        self.assertEqual(script["name"], "Test Script 1")
        self.assertEqual(script["category"], "test")
        
        # Ищем несуществующий скрипт
        script = self.searcher.find_script_by_name("Nonexistent Script")
        self.assertIsNone(script)
    
    def test_find_scripts_by_category(self):
        """Тест поиска скриптов по категории."""
        # Ищем скрипты в существующей категории
        scripts = self.searcher.find_scripts_by_category("test")
        self.assertEqual(len(scripts), 2)
        
        # Ищем скрипты в несуществующей категории
        scripts = self.searcher.find_scripts_by_category("nonexistent")
        self.assertEqual(len(scripts), 0)
    
    def test_get_all_scripts(self):
        """Тест получения всех скриптов."""
        scripts = self.searcher.get_all_scripts()
        self.assertEqual(len(scripts), 3)
    
    def test_get_all_categories(self):
        """Тест получения всех категорий."""
        categories = self.searcher.get_all_categories()
        self.assertEqual(len(categories), 2)
        self.assertIn("test", categories)
        self.assertIn("another", categories)
    
    def test_delete_script(self):
        """Тест удаления скрипта."""
        # Удаляем существующий скрипт
        result = self.searcher.delete_script("Test Script 1")
        self.assertTrue(result)
        
        # Проверяем, что скрипт удален
        script = self.searcher.find_script_by_name("Test Script 1")
        self.assertIsNone(script)
        
        # Удаляем несуществующий скрипт
        result = self.searcher.delete_script("Nonexistent Script")
        self.assertFalse(result)
    
    def test_search_in_scripts(self):
        """Тест полнотекстового поиска."""
        # Поиск по содержимому
        scripts = self.searcher.search_in_scripts("id = 1")
        self.assertEqual(len(scripts), 2)
        
        # Поиск по названию
        scripts = self.searcher.search_in_scripts("Another")
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0]["name"], "Another Script")
        
        # Поиск по описанию
        scripts = self.searcher.search_in_scripts("description 2")
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0]["name"], "Test Script 2")
    
    def test_update_script(self):
        """Тест обновления скрипта."""
        # Обновляем существующий скрипт
        new_content = "SELECT * FROM test WHERE id = 2"
        result = self.searcher.update_script("Test Script 1", new_content)
        self.assertTrue(result)
        
        # Проверяем, что содержимое обновлено
        script = self.searcher.find_script_by_name("Test Script 1")
        self.assertEqual(script["content"], new_content)
        self.assertEqual(script["version"], 2)
        
        # Проверяем, что история версий создана
        versions = self.searcher.get_script_history("Test Script 1")
        self.assertEqual(len(versions), 2)
        
        # Обновляем несуществующий скрипт
        result = self.searcher.update_script("Nonexistent Script", "SELECT 1")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 