import asyncio
import schedule
import time
from datetime import datetime
import pytz
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import Config
from .weather import WeatherService
from .vk_poster import VKPoster

class WeatherBot:
    """Основной класс бота"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        self.weather_service = WeatherService()
        self.vk_poster = VKPoster()
        self.timezone = pytz.timezone(self.config.TIMEZONE)
        self.running = True
        
    async def post_weather(self):
        """
        Получает погоду и публикует пост
        """
        current_time = self._get_current_time()
        print(f"\n🔄 Запуск публикации в {current_time}")
        
        # Получаем погоду
        weather_data = self.weather_service.get_weather()
        
        if not weather_data:
            print("❌ Не удалось получить данные о погоде")
            return
        
        # Форматируем сообщение
        message = self.weather_service.format_weather_message(weather_data)
        
        # Выводим сообщение в консоль для проверки
        print("\n📝 Текст поста:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        
        # Публикуем пост
        success = await self.vk_poster.post_to_wall(message)
        
        if success:
            print("✅ Публикация завершена успешно")
        else:
            print("❌ Ошибка при публикации")
    
    def _get_current_time(self):
        """Возвращает текущее время в часовом поясе бота"""
        return datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    def schedule_jobs(self):
        """Настраивает расписание публикаций"""
        post_time = self.config.POST_TIME
        
        # Планируем ежедневную публикацию
        schedule.every().day.at(post_time).do(
            lambda: asyncio.create_task(self.post_weather())
        )
        
        print(f"📅 Бот запущен. Публикация запланирована ежедневно в {post_time} ({self.config.TIMEZONE})")
        
    async def run(self):
        """Запускает бота"""
        print("\n" + "="*50)
        print("🚀 ЗАПУСК БОТА ПОГОДЫ ДЛЯ ВКОНТАКТЕ")
        print("="*50)
        print(f"📍 Координаты СНТ: {self.config.LAT}, {self.config.LON}")
        print(f"🌍 Часовой пояс: {self.config.TIMEZONE}")
        print("="*50 + "\n")
        
        # Настраиваем расписание
        self.schedule_jobs()
        
        # Выполняем немедленную публикацию при запуске (для теста)
        print("📢 Тестовая публикация при запуске:")
        await self.post_weather()
        
        print("\n⏳ Ожидание следующего запланированного запуска...")
        print("🔍 Для остановки нажмите Ctrl+C\n")
        
        # Бесконечный цикл проверки расписания
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)  # Проверяем каждую минуту

def main():
    """Точка входа"""
    bot = WeatherBot()
    
    try:
        # Запускаем асинхронный цикл
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()