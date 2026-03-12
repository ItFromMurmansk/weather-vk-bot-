from vkbottle import API
from vkbottle.api import API
from vkbottle.exception_factory import VKAPIError
from .config import Config
from datetime import datetime, timedelta
from typing import Optional
import json
import os

class VKPoster:
    """Класс для публикации и обновления постов в группе ВКонтакте"""
    
    def __init__(self):
        self.token = Config.VK_TOKEN
        self.group_id = int(Config.VK_GROUP_ID)
        self.api = API(token=self.token)
        self.post_id_file = "last_post_id.txt"  # Файл для хранения ID поста
        
    def save_post_id(self, post_id: int):
        """Сохраняет ID поста в файл"""
        try:
            with open(self.post_id_file, 'w') as f:
                f.write(str(post_id))
            print(f"💾 Сохранен ID поста: {post_id}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении ID: {e}")
    
    def load_post_id(self) -> Optional[int]:
        """Загружает ID поста из файла"""
        try:
            if os.path.exists(self.post_id_file):
                with open(self.post_id_file, 'r') as f:
                    post_id = int(f.read().strip())
                print(f"📂 Загружен ID поста: {post_id}")
                return post_id
        except Exception as e:
            print(f"❌ Ошибка при загрузке ID: {e}")
        return None
    
    async def update_post(self, message: str) -> bool:
        """
        Обновляет существующий пост или создает новый
        """
        try:
            # Пытаемся загрузить ID существующего поста
            post_id = self.load_post_id()
            
            if post_id:
                # Пробуем обновить существующий пост
                try:
                    # В VK нельзя напрямую обновить пост, поэтому удаляем и создаем новый
                    await self.api.wall.delete(
                        owner_id=-self.group_id,
                        post_id=post_id
                    )
                    print(f"🗑️ Удален старый пост (ID: {post_id})")
                    
                    # Создаем новый пост
                    result = await self.api.wall.post(
                        owner_id=-self.group_id,
                        message=message,
                        from_group=1
                    )
                    
                    # Сохраняем новый ID
                    self.save_post_id(result.post_id)
                    print(f"✅ Пост обновлен в {datetime.now().strftime('%H:%M')}")
                    print(f"📎 Новый ID поста: {result.post_id}")
                    return True
                    
                except VKAPIError as e:
                    if e.code == 103:  # Пост не найден
                        print("ℹ️ Старый пост не найден, создаем новый")
                        post_id = None
                    else:
                        raise e
            
            # Если нет поста или он был удален - создаем новый
            if not post_id:
                result = await self.api.wall.post(
                    owner_id=-self.group_id,
                    message=message,
                    from_group=1
                )
                self.save_post_id(result.post_id)
                print(f"✅ Создан новый пост в {datetime.now().strftime('%H:%M')}")
                print(f"📎 ID поста: {result.post_id}")
                return True
                
        except VKAPIError as e:
            print(f"❌ Ошибка VK API: {e}")
            if e.code == 15:
                print("   ❗ Нет прав на публикацию/удаление")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False