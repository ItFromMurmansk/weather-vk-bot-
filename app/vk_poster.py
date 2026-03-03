from vkbottle import API
from vkbottle.exception import VKAPIError
from .config import Config
from datetime import datetime

class VKPoster:
    """Класс для публикации постов в группе ВКонтакте"""
    
    def __init__(self):
        self.token = Config.VK_TOKEN
        self.group_id = int(Config.VK_GROUP_ID)
        self.api = API(token=self.token)
        
    async def post_to_wall(self, message: str) -> bool:
        """
        Публикует пост на стене сообщества
        
        Args:
            message: Текст поста
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            # Публикуем пост на стене (owner_id должен быть отрицательным для группы)
            result = await self.api.wall.post(
                owner_id=-self.group_id,
                message=message,
                from_group=1  # Публикуем от имени группы
            )
            
            print(f"✅ Пост успешно опубликован в {datetime.now().strftime('%H:%M:%S')}")
            print(f"📎 ID поста: {result.post_id}")
            return True
            
        except VKAPIError as e:
            print(f"❌ Ошибка VK API: {e}")
            if e.code == 15:
                print("   ❗ Нет прав на публикацию. Проверьте токен и права доступа")
            elif e.code == 214:
                print("   ❗ Пост уже был опубликован сегодня (дубликат)")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False