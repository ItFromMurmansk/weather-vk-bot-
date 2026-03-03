import requests
from datetime import datetime
from typing import Dict, Any, Optional
from .config import Config

class WeatherService:
    """Сервис для получения данных о погоде с OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = Config.WEATHER_API_URL
        self.lat = Config.LAT
        self.lon = Config.LON
        
    def get_weather(self) -> Optional[Dict[str, Any]]:
        """
        Получает текущую погоду по координатам СНТ
        
        Returns:
            Dict с данными о погоде или None в случае ошибки
        """
        try:
            # Параметры запроса к OpenWeatherMap
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'metric',  # Температура в Цельсиях
                'lang': 'ru'         # Описание на русском
            }
            
            print(f"🌤 Запрос погоды для координат: {self.lat}, {self.lon}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе к API погоды: {e}")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return None
    
    def _parse_weather_data(self, data: Dict) -> Dict[str, Any]:
        """
        Преобразует сырые данные от API в удобный формат
        """
        # Основные метеоданные
        main = data.get('main', {})
        wind = data.get('wind', {})
        weather = data.get('weather', [{}])[0]
        sys = data.get('sys', {})
        
        # Температура
        temp = main.get('temp', 0)
        wind_speed = wind.get('speed', 0)
        
        # Ощущаемая температура с учетом ветра (формула для холодной погоды)
        if temp < 10 and wind_speed > 1.5:
            # Ветро-холодовой индекс
            feels_like = 13.12 + 0.6215 * temp - 11.37 * (wind_speed ** 0.16) + 0.3965 * temp * (wind_speed ** 0.16)
        else:
            feels_like = main.get('feels_like', temp)
        
        # Код погоды для эмодзи
        weather_id = weather.get('id', 800)
        
        return {
            'temperature': round(temp, 1),
            'feels_like': round(feels_like, 1),
            'pressure': round(main.get('pressure', 0) * 0.750062),  # гПа -> мм рт. ст.
            'humidity': main.get('humidity', 0),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': self._get_wind_direction(wind.get('deg', 0)),
            'description': weather.get('description', ''),
            'emoji': self._get_weather_emoji(weather_id),
            'clouds': data.get('clouds', {}).get('all', 0),
            'sunrise': datetime.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M'),
            'city': data.get('name', 'СНТ')
        }
    
    def _get_weather_emoji(self, weather_id: int) -> str:
        """Возвращает эмодзи в зависимости от кода погоды"""
        if weather_id == 800:
            return "☀️"  # Ясно
        elif 801 <= weather_id <= 802:
            return "🌤️"  # Малооблачно
        elif 803 <= weather_id <= 804:
            return "☁️"  # Облачно
        elif 700 <= weather_id < 800:
            return "🌫️"  # Туман
        elif 600 <= weather_id < 700:
            return "🌨️"  # Снег
        elif 500 <= weather_id < 600:
            return "🌧️"  # Дождь
        elif 300 <= weather_id < 400:
            return "🌦️"  # Морось
        elif 200 <= weather_id < 300:
            return "⛈️"  # Гроза
        else:
            return "🌡️"  # Термометр для непонятной погоды
    
    def _get_wind_direction(self, degrees: float) -> str:
        """Преобразует градусы ветра в текстовое направление"""
        if degrees is None:
            return "штиль"
        
        directions = [
            'северный', 'северо-восточный', 'восточный', 'юго-восточный',
            'южный', 'юго-западный', 'западный', 'северо-западный'
        ]
        index = round(degrees / 45) % 8
        return directions[index]
    
    def format_weather_message(self, weather_data: Dict[str, Any]) -> str:
        """
        Форматирует данные о погоде в красивый текст для поста
        """
        if not weather_data:
            return "😔 Не удалось получить данные о погоде. Попробуйте позже."
        
        # Определяем дополнительные эмодзи для параметров
        wind_emoji = "💨" if weather_data['wind_speed'] > 5 else "🍃"
        
        # Тренд давления (условно)
        if weather_data['pressure'] > 760:
            pressure_emoji = "📈"
        elif weather_data['pressure'] < 750:
            pressure_emoji = "📉"
        else:
            pressure_emoji = "➡️"
        
        # Формируем сообщение
        message = f"""
{weather_data['emoji']} **Доброе утро, садоводы!**

Погода в нашем СНТ на сегодня:

🌡 **Температура:** {weather_data['temperature']}°C
👕 **Ощущается как:** {weather_data['feels_like']}°C

{wind_emoji} **Ветер:** {weather_data['wind_speed']} м/с, {weather_data['wind_direction']}
💧 **Влажность:** {weather_data['humidity']}%
{pressure_emoji} **Давление:** {weather_data['pressure']} мм рт.ст.
☁️ **Облачность:** {weather_data['clouds']}%

📝 **Описание:** {weather_data['description'].capitalize()}

🌅 **Рассвет:** {weather_data['sunrise']}
🌇 **Закат:** {weather_data['sunset']}

🍃 Хорошего дня и отличного настроения! 🌿
"""
        return message.strip()