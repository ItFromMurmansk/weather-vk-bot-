import asyncio
import schedule
from datetime import datetime, time
import pytz
import sys
import os

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
        Получает погоду и обновляет пост
        """
        current_time = self._get_current_time()
        print(f"\n🔄 Обновление погоды в {current_time}")
        
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
        
        # Обновляем пост
        success = await self.vk_poster.update_post(message)
        
        if success:
            print("✅ Пост успешно обновлен")
        else:
            print("❌ Ошибка при обновлении поста")
    
    def _get_current_time(self):
        """Возвращает текущее время в часовом поясе бота"""
        return datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
    
    def should_run_now(self) -> bool:
        """
        Проверяет, нужно ли запускать обновление в текущее время
        (с 8:00 до 21:00 каждый час)
        """
        now = datetime.now(self.timezone)
        current_hour = now.hour
        
        # Проверяем, что время между 8:00 и 21:00
        return 8 <= current_hour <= 21
    
    def schedule_jobs(self):
        """Настраивает расписание публикаций"""
        
        # Запускаем каждый час с 8:00 до 21:00
        for hour in range(8, 22):  # 8:00, 9:00, ... 21:00
            schedule.every().day.at(f"{hour:02d}:00").do(
                lambda: asyncio.create_task(self.post_weather())
            )
        
        print(f"📅 Бот запущен. Обновление поста каждый час с 8:00 до 21:00")
        print(f"🕐 Текущее время: {datetime.now(self.timezone).strftime('%H:%M')}")
        
    async def run(self):
        """Запускает бота"""
        print("\n" + "="*50)
        print("🚀 ЗАПУСК БОТА ПОГОДЫ ДЛЯ ВКОНТАКТЕ (HOURLY MODE)")
        print("="*50)
        print(f"📍 Координаты СНТ: {self.config.LAT}, {self.config.LON}")
        print(f"🌍 Часовой пояс: {self.config.TIMEZONE}")
        print("="*50 + "\n")
        
        # Настраиваем расписание
        self.schedule_jobs()
        
        # Если сейчас время между 8 и 21 - делаем немедленное обновление
        if self.should_run_now():
            print("📢 Первое обновление сейчас:")
            await self.post_weather()
        else:
            print(f"⏳ Сейчас {datetime.now(self.timezone).strftime('%H:%M')} - ожидание 8:00...")
        
        print("\n⏳ Ожидание следующего обновления...")
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