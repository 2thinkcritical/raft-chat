"""Модуль для загрузки промптов из текстовых файлов."""

import os
from pathlib import Path
from typing import Optional


class PromptLoader:
    """Загрузчик промптов из текстовых файлов."""

    def __init__(self, prompts_dir: str = "prompts"):
        """Инициализация загрузчика промптов.

        Args:
            prompts_dir: Путь к директории с промптами
        """
        self.prompts_dir = Path(prompts_dir)
        self._prompts_cache: dict[str, str] = {}

    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """Загружает промпт по имени файла.

        Args:
            prompt_name: Имя файла промпта (без расширения .txt)

        Returns:
            Содержимое промпта или None, если файл не найден
        """
        # Проверяем кэш
        if prompt_name in self._prompts_cache:
            return self._prompts_cache[prompt_name]

        # Формируем путь к файлу
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"

        if not prompt_file.exists():
            return None

        try:
            # Читаем содержимое файла
            with open(prompt_file, encoding="utf-8") as f:
                content = f.read().strip()

            # Кэшируем промпт
            self._prompts_cache[prompt_name] = content
            return content

        except Exception as e:
            print(f"Ошибка при чтении промпта {prompt_name}: {e}")
            return None

    def reload_prompts(self) -> None:
        """Перезагружает все промпты из файлов."""
        self._prompts_cache.clear()

    def list_available_prompts(self) -> list[str]:
        """Возвращает список доступных промптов.

        Returns:
            Список имен доступных промптов
        """
        if not self.prompts_dir.exists():
            return []

        prompt_files = list(self.prompts_dir.glob("*.txt"))
        return [f.stem for f in prompt_files]

    def prompt_exists(self, prompt_name: str) -> bool:
        """Проверяет, существует ли промпт с указанным именем.

        Args:
            prompt_name: Имя промпта

        Returns:
            True, если промпт существует
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        return prompt_file.exists()


# Создаем глобальный экземпляр загрузчика
# Путь к папке prompts (работает и локально, и в Docker)


def get_prompts_directory() -> str:
    """Определяет путь к папке с промптами."""
    # Папка prompts теперь всегда находится в app/prompts
    # Это работает и локально, и в Docker
    current_dir = os.path.dirname(__file__)
    prompts_path = os.path.join(current_dir, "prompts")
    return prompts_path


prompts_dir = get_prompts_directory()
prompt_loader = PromptLoader(prompts_dir)


def get_prompt(prompt_name: str) -> Optional[str]:
    """Удобная функция для получения промпта.

    Args:
        prompt_name: Имя промпта

    Returns:
        Содержимое промпта или None
    """
    return prompt_loader.get_prompt(prompt_name)


def reload_prompts() -> None:
    """Перезагружает все промпты."""
    prompt_loader.reload_prompts()


def list_prompts() -> list[str]:
    """Возвращает список доступных промптов.

    Returns:
        Список имен промптов
    """
    return prompt_loader.list_available_prompts()


def prompt_exists(prompt_name: str) -> bool:
    """Проверяет, существует ли промпт.

    Args:
        prompt_name: Имя промпта

    Returns:
        True, если промпт существует
    """
    return prompt_loader.prompt_exists(prompt_name)


# Пример использования
if __name__ == "__main__":
    print("Доступные промпты:")
    for prompt_name in list_prompts():
        print(f"  - {prompt_name}")

    print("\nТестирование загрузки:")
    test_prompt = get_prompt("rag_prompt")
    if test_prompt:
        print(f"✅ rag_prompt загружен (длина: {len(test_prompt)} символов)")
    else:
        print("❌ Ошибка загрузки промпта")
