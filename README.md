
### `README.md`


# GreenApiTests

Тестовый проект для проверки методов API GreenAPI: `SendMessage` и `GetChatHistory`. Написан на Python с использованием `pytest` и `requests_mock` для автоматизированного тестирования.

## Описание

Проект содержит юнит-тесты для двух методов GreenAPI:
- **`SendMessage`**: Отправка сообщений в личные и групповые чаты WhatsApp.
- **`GetChatHistory`**: Получение истории сообщений чата.

Тесты полностью замоканы с использованием `requests_mock`, что делает их независимыми от реальных сетевых запросов и лимитов API. Конфиденциальные данные (ID инстанса, токен API) вынесены в файл `.env`.

## Структура проекта

![image](https://github.com/user-attachments/assets/0d955d9f-4d71-4b23-8247-578113f8d7eb)


## Установка

### Требования
- Python 3.8+
- Git

### Шаги
1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/Sotren/GreenApiTests.git
   cd GreenApiTests
  

2. **Установите зависимости**:
   ```bash
   pip install requests pytest requests-mock python-dotenv
  

3. **Настройте окружение**:
   - Создайте файл `.env` в корне проекта.
   - Добавьте данные из личного кабинета GreenAPI:
     ```
     INSTANCE_ID=ваш_instance_id
     API_TOKEN=ваш_api_token
     VALID_CHAT_ID=ваш_VALID_CHAT_ID@c.us
     VALID_GROUP_ID=ваш_VALID_GROUP_ID@g.us
     VALID_QUOTED_MESSAGE_ID=361B0E63F2FDF95903B6A9C9A102F34B
     VALID_MESSAGE=Hello from automated test!
     ```
   - **Важно**: Замените значения на свои. Тесты замоканы, поэтому они работают с любыми данными. Однако для реальных запросов к GreenAPI (если вы уберете мокирование) нужны валидные значения, так как бесплатная версия GreenAPI может блокировать запросы при превышении лимитов.

## Запуск тестов

1. **Все тесты**:
   ```bash
   pytest -v
   ```
    ![image](https://github.com/user-attachments/assets/6eac5532-c70b-4a0d-865d-d5fd9eecbbe4)
   - Ожидаемый вывод: `17 passed (9 тестов для `SendMessage`, 6 для `GetChatHistory`, включая 3 параметризованных).

2. **Тесты для одного метода**:
   - `SendMessage`:
     ```bash
     pytest test_send_message.py -v
     ```
      ![image](https://github.com/user-attachments/assets/eddbad5e-f81d-4915-8948-5144c95714fd)

   - `GetChatHistory`:
     ```bash
     pytest test_get_chat_history.py -v
     ```
       ![image](https://github.com/user-attachments/assets/0c74e22d-4851-440d-8b81-73345a6348ee)
## Тесты

### SendMessage
- **Успешные сценарии**: Отправка в личный чат, групповой чат, с цитированием.
- **Негативные сценарии**: Длинное сообщение (>20k символов), невалидный `chatId` (3 случая), неверный `quotedMessageId`, пустое сообщение, неверный токен, таймаут.

### GetChatHistory
- **Успешный сценарий**: Получение истории чата.
- **Негативные сценарии**: Неверный `chatId`, пустой `chatId`, некорректный `count`, неверный токен, таймаут.

## Зависимости

- `requests`: Для работы с HTTP (в `requests_mock`).
- `pytest`: Фреймворк тестирования.
- `requests-mock`: Мокирование запросов.
- `python-dotenv`: Загрузка `.env`.

## Проверка реальных данных

### Если вы хотите протестировать реальные запросы к GreenAPI вместо замоканных тестов, выполните следующие изменения в коде:

Шаги
Удалите мокирование:
- В test_send_message.py и test_get_chat_history.py:
- Удалите строку: import requests_mock
- Уберите все блоки with requests_mock.Mocker() as m: и связанные с ними строки m.post(...). Например:
-  Было:
 ```bash
def test_send_message_success(api_client, api_config, valid_chat_id, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], json={"idMessage": "mocked_id"}, status_code=200)
        payload = {"chatId": valid_chat_id, "message": valid_message}
        response = api_client("send", payload)
        assert response.status_code == 200, "Ошибка: статус не 200"
        assert "idMessage" in response.json(), "Ошибка: нет idMessage в ответе"
 ```
- Станет:
 ```bash
def test_send_message_success(api_client, api_config, valid_chat_id, valid_message):
    payload = {"chatId": valid_chat_id, "message": valid_message}
    response = api_client("send", payload)
    assert response.status_code == 200, "Ошибка: статус не 200"
    assert "idMessage" in response.json(), "Ошибка: нет idMessage в ответе"
 ``` 
### Повторите для всех тестов в обоих файлах.
 
### Обработайте тесты с таймаутом:
- Тесты test_send_message_timeout и test_get_chat_history_timeout зависят от мокирования таймаутов. Удалите их или закомментируйте:
 ```bash
 def test_send_message_timeout(api_client, api_config, valid_chat_id, valid_message):
    payload = {"chatId": valid_chat_id, "message": valid_message}
    with pytest.raises(pytest.fail.Exception, match="API request timed out"):
        api_client("send", payload)
```
### Обновите .env:
- Убедитесь, что все значения в .env валидны и соответствуют вашему аккаунту GreenAPI. Неверные данные приведут к ошибкам вроде 401 Unauthorized или 429 Too Many Requests.
- Запустите тесты:
