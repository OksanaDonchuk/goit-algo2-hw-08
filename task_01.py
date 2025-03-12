import random
import time
from typing import Dict
from collections import deque


class SlidingWindowRateLimiter:
       
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        Ініціалізація rate limiter з заданими параметрами.

        :param window_size: Часове вікно в секундах
        :param max_requests: Максимальна кількість повідомлень у вікні
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests: Dict[str, deque] = {}
        self.blocked_requests = 0  # Лічильник заблокованих запитів

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Видаляє застарілі запити користувача, що вийшли за межі часового вікна.
        
        :param user_id: ID користувача
        :param current_time: Поточний час у секундах
        """
        if user_id in self.user_requests:
            while self.user_requests[user_id] and self.user_requests[user_id][0] <= current_time - self.window_size:
                self.user_requests[user_id].popleft()

            if not self.user_requests[user_id]:  # Видалення користувача, якщо список запитів порожній
                del self.user_requests[user_id]

    def can_send_message(self, user_id: str, current_time: float) -> bool:
        """
        Перевіряє, чи може користувач відправити повідомлення у поточному часовому вікні.

        :param user_id: ID користувача
        :return: True, якщо можна відправити повідомлення, інакше False
        """
        self._cleanup_window(user_id, current_time)
        return user_id not in self.user_requests or len(self.user_requests[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Записує нове повідомлення для користувача, якщо дозволено.
        
        :param user_id: ID користувача
        :return: True, якщо повідомлення дозволено, False, якщо заблоковано
        """
        current_time = time.time()
        if self.can_send_message(user_id, current_time):
            if user_id not in self.user_requests:
                self.user_requests[user_id] = deque()
            self.user_requests[user_id].append(current_time)
            return True
        
        self.blocked_requests += 1  # Лічильник заблокованих запитів
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Обчислює час, що залишився до наступного дозволеного повідомлення.
        
        :param user_id: ID користувача
        :return: Час у секундах до наступного дозволеного повідомлення
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_requests or len(self.user_requests[user_id]) < self.max_requests:
            return 0.0

        return max(0.0, self.user_requests[user_id][0] + self.window_size - current_time)


# Демонстрація роботи Rate Limiter
def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        status = "✓" if result else f"× (очікування {wait_time:.1f}с)"
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")

        time.sleep(random.uniform(0.1, 1.0))  # Додаємо затримку

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        status = "✓" if result else f"× (очікування {wait_time:.1f}с)"
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")

        time.sleep(random.uniform(0.1, 1.0))

    print(f"\nЗагальна кількість заблокованих запитів: {limiter.blocked_requests}")


if __name__ == "__main__":
    test_rate_limiter()