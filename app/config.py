import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    """Конфигурация бота погоды для ВКонтакте"""
    
    # ВКонтакте
    VK_TOKEN = os.getenv('VK_TOKEN')
    VK_GROUP_ID = os.getenv('VK_GROUP_ID')
    
    # OpenWeatherMap
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    WEATHER_API_URL = os.getenv('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5/weather')
    
    # Координаты СНТ (по умолчанию - Кандалакшский залив)
    LAT = float(os.getenv('LAT', '67.132386'))
    LON = float(os.getenv('LON', '32.127069'))
    
    # Время публикации
    POST_TIME = os.getenv('POST_TIME', '08:00')
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Moscow')
    
    @classmethod
    def validate(cls):
        """Проверяет наличие обязательных переменных"""
        required_vars = ['VK_TOKEN', 'VK_GROUP_ID', 'WEATHER_API_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(
                f"❌ Отсутствуют обязательные переменные в .env: {', '.join(missing)}\n"
                f"Скопируйте .env.example в .env и заполните данные"
            )
        
        print("✅ Конфигурация загружена успешно")
        return True