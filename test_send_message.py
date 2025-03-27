import pytest
import requests_mock
import requests

from conftest import logger, assert_validation_error

# ✅ 1. Успешная отправка сообщения в личный чат
# Проверяет, что сообщение отправляется и возвращается idMessage
def test_send_message_success(api_client, api_config, valid_chat_id, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], json={"idMessage": "mocked_id"}, status_code=200)
        payload = {"chatId": valid_chat_id, "message": valid_message}
        response = api_client("send", payload)
        assert response.status_code == 200, "Ошибка: статус не 200"
        assert "idMessage" in response.json(), "Ошибка: нет idMessage в ответе"

# ✅ 2. Успешная отправка сообщения в групповой чат
# Тестирует отправку сообщения в группу с валидным groupId
def test_send_group_message(api_client, api_config, valid_group_id, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], json={"idMessage": "mocked_id"}, status_code=200)
        payload = {"chatId": valid_group_id, "message": valid_message}
        response = api_client("send", payload)
        assert response.status_code == 200, "Ошибка: статус не 200"
        assert "idMessage" in response.json(), "Ошибка: нет idMessage в ответе"

# ✅ 3. Отправка сообщения с цитированием
# Проверяет успешную отправку с валидным quotedMessageId
def test_send_message_with_quote(api_client, api_config, valid_chat_id, valid_message, valid_quoted_message_id):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], json={"idMessage": "mocked_id"}, status_code=200)
        payload = {"chatId": valid_chat_id, "message": valid_message, "quotedMessageId": valid_quoted_message_id}
        response = api_client("send", payload)
        assert response.status_code == 200, "Ошибка: статус не 200"
        assert "idMessage" in response.json(), "Ошибка: нет idMessage в ответе"

# ❌ 4. Ошибка: слишком длинное сообщение
# Тестирует, что API отклоняет сообщение длиннее 20 000 символов
def test_send_too_long_message(api_client, api_config, valid_chat_id):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], status_code=400, text='{"error": "Validation failed"}')
        payload = {"chatId": valid_chat_id, "message": "A" * 20001}
        response = api_client("send", payload)
        assert_validation_error(response)

# ❌ 5. Ошибка: неверный chatId
# Проверяет обработку разных невалидных chatId (параметризованный тест)
@pytest.mark.parametrize(
    "chat_id, expected_status, expected_error",
    [
        ("invalid_chat", 400, "Validation failed"),  # Неверный формат chatId
        ("00000000000@c.us", 400, "'chatId' does not exist"),  # Несуществующий чат
        ("", 400, "Validation failed"),  # Пустой chatId
    ]
)
def test_invalid_chat_id(api_client, api_config, chat_id, expected_status, expected_error, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], status_code=expected_status, text=f'{{"error": "{expected_error}"}}')
        payload = {"chatId": chat_id, "message": valid_message}
        response = api_client("send", payload)
        assert_validation_error(response, expected_status, expected_error)

# ❌ 6. Ошибка: неверный quotedMessageId
# Проверяет, что API отклоняет невалидный quotedMessageId
def test_send_invalid_quoted_message(api_client, api_config, valid_chat_id, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], status_code=400, text='{"error": "Validation failed"}')
        payload = {"chatId": valid_chat_id, "message": valid_message, "quotedMessageId": "INVALID_ID"}
        response = api_client("send", payload)
        assert_validation_error(response)

# ❌ 7. Ошибка: пустое сообщение
# Тестирует, что API не принимает пустой текст сообщения
def test_send_empty_message(api_client, api_config, valid_chat_id):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], status_code=400, text='{"error": "Validation failed"}')
        payload = {"chatId": valid_chat_id, "message": ""}
        response = api_client("send", payload)
        assert_validation_error(response)

# ❌ 8. Ошибка: отправка с неверным токеном
# Проверяет, что API возвращает 401 при невалидном токене
def test_send_message_invalid_token(api_client, api_config, valid_chat_id, valid_message):
    invalid_url = f"https://7105.api.greenapi.com/waInstance{api_config['instance_id']}/SendMessage/INVALID_TOKEN"
    with requests_mock.Mocker() as m:
        m.post(invalid_url, status_code=401, text='{"error": "Unauthorized"}')
        payload = {"chatId": valid_chat_id, "message": valid_message}
        response = api_client("send", payload, url=invalid_url)
        assert response.status_code == 401, "Ошибка: ожидаем 401 Unauthorized"

# ❌ 9. Ошибка: таймаут запроса
# Проверяет обработку случая, когда API не отвечает вовремя
def test_send_message_timeout(api_client, api_config, valid_chat_id, valid_message):
    with requests_mock.Mocker() as m:
        m.post(api_config["send_url"], exc=requests.exceptions.Timeout)
        payload = {"chatId": valid_chat_id, "message": valid_message}
        with pytest.raises(pytest.fail.Exception, match="API request timed out"):
            api_client("send", payload)

if __name__ == "__main__":
    pytest.main()