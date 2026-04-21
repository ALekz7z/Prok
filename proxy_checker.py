#!/usr/bin/env python3
"""
Программа для автоматической проверки прокси из списка.
Проверяет работоспособность прокси и выводит результаты.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Список прокси для проверки (формат: "ip:port" или "ip:port:username:password")
PROXY_LIST = [
    "127.0.0.1:8080",
    # Добавьте свои прокси сюда
]

# Тестовый URL для проверки
TEST_URL = "https://httpbin.org/ip"

# Таймаут подключения в секундах
TIMEOUT = 5


def check_proxy(proxy):
    """
    Проверяет работоспособность прокси.
    
    Args:
        proxy: Строка в формате "ip:port" или "ip:port:username:password"
    
    Returns:
        dict: Результат проверки (working, response_time, error)
    """
    result = {
        "proxy": proxy,
        "working": False,
        "response_time": None,
        "error": None
    }
    
    try:
        # Парсинг прокси
        parts = proxy.split(":")
        
        if len(parts) == 2:
            # Прокси без авторизации: ip:port
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
        elif len(parts) == 4:
            # Прокси с авторизацией: ip:port:username:password
            ip, port, username, password = parts
            proxies = {
                "http": f"http://{username}:{password}@{ip}:{port}",
                "https": f"http://{username}:{password}@{ip}:{port}"
            }
        else:
            result["error"] = "Неверный формат прокси"
            return result
        
        start_time = time.time()
        
        response = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=TIMEOUT
        )
        
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        
        if response.status_code == 200:
            result["working"] = True
            result["response_time"] = response_time
        else:
            result["error"] = f"HTTP {response.status_code}"
            
    except requests.exceptions.ProxyError as e:
        result["error"] = "Proxy Error"
    except requests.exceptions.ConnectTimeout as e:
        result["error"] = "Connect Timeout"
    except requests.exceptions.ReadTimeout as e:
        result["error"] = "Read Timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    print("=" * 60)
    print("Проверка прокси")
    print("=" * 60)
    print(f"Тестовый URL: {TEST_URL}")
    print(f"Таймаут: {TIMEOUT} сек")
    print(f"Всего прокси: {len(PROXY_LIST)}")
    print("=" * 60)
    
    if not PROXY_LIST:
        print("\nСписок прокси пуст! Добавьте прокси в переменную PROXY_LIST.")
        return
    
    working_proxies = []
    results = []
    
    # Проверка прокси с использованием многопоточности
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {
            executor.submit(check_proxy, proxy): proxy 
            for proxy in PROXY_LIST
        }
        
        for i, future in enumerate(as_completed(future_to_proxy), 1):
            result = future.result()
            results.append(result)
            
            status = "✓ РАБОЧИЙ" if result["working"] else "✗ НЕ РАБОЧИЙ"
            print(f"[{i}/{len(PROXY_LIST)}] {result['proxy']}")
            print(f"    Статус: {status}")
            
            if result["working"]:
                print(f"    Время ответа: {result['response_time']} сек")
                working_proxies.append(result["proxy"])
            else:
                print(f"    Ошибка: {result['error']}")
            print()
    
    # Итоговая статистика
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    print(f"Всего проверено: {len(PROXY_LIST)}")
    print(f"Рабочих: {len(working_proxies)}")
    print(f"Не рабочих: {len(PROXY_LIST) - len(working_proxies)}")
    
    if working_proxies:
        print("\nРабочие прокси:")
        for proxy in working_proxies:
            print(f"  - {proxy}")
    
    # Сохранение рабочих прокси в файл
    if working_proxies:
        with open("working_proxies.txt", "w") as f:
            f.write("\n".join(working_proxies))
        print(f"\nРабочие прокси сохранены в файл: working_proxies.txt")


if __name__ == "__main__":
    main()
