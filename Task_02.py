import time
from typing import Dict
import random


class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        """
        Ініціалізує лімітера з вказаним мінімальним інтервалом між повідомленнями.
        :param min_interval: Мінімальний інтервал між повідомленнями в секундах.
        """
        self.min_interval = min_interval
        self.user_last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може користувач відправити повідомлення.
        :param user_id: ID користувача.
        :return: True, якщо повідомлення дозволено, інакше False.
        """
        current_time = time.time()
        last_message_time = self.user_last_message_time.get(user_id, 0)
        return (current_time - last_message_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Записує повідомлення користувача, якщо це дозволено.
        :param user_id: ID користувача.
        :return: True, якщо повідомлення записано, інакше False.
        """
        current_time = time.time()
        last_message_time = self.user_last_message_time.get(user_id, 0)
    
        if (current_time - last_message_time) >= self.min_interval:
            self.user_last_message_time[user_id] = current_time
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Обчислює час до можливості відправлення наступного повідомлення.
        :param user_id: ID користувача.
        :return: Час очікування в секундах.
        """
        current_time = time.time()
        last_message_time = self.user_last_message_time.get(user_id, 0)
        wait_time = self.min_interval - (current_time - last_message_time)
        return max(0.0, wait_time)


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_throttling_limiter()