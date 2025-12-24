import asyncio

async def send_email(to: str, subject: str, body: str):
    """
    Функция отправки email.
    В тестовом режиме просто выводит информацию в консоль.
    """
    # Выводим в консоль для тестирования
    print(f"\n{'='*60}")
    print(f"EMAIL TO: {to}")
    print(f"SUBJECT: {subject}")
    print(f"BODY:")
    print(body)
    print(f"{'='*60}\n")
    
    # Имитируем небольшую задержку отправки
    await asyncio.sleep(0.1)
    
    # В тестовом режиме всегда возвращаем успех
    return True