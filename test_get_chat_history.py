import pytest
import requests_mock
import requests

from conftest import logger, assert_validation_error

# ✅ 1. Успешное получение истории чата
# Проверяет, что метод возвращает список сообщений для валидного chatId
def test_get_chat_history_success(api_client, api_config, valid_chat_id):
    with requests_mock.Mocker() as m:
        mock_response = [{"type": "incoming", "idMessage": "mocked_id", "timestamp": 1706522263}]
        m.post(api_config["history_url"], json=mock_response, status_code=200)
        payload = {"chatId": valid_chat_id, "count": 10}
        response = api_client("history", payload)
        assert response.status_code == 200, "Ошибка: статус не 200"
        assert isinstance(response.json(), list), "Ошибка: ответ должен быть списком"
        assert "type" in response.json()[0], "Ошибка: нет поля type"
        assert "idMessage" in response.json()[0], "Ошибка: нет поля idMessage"

# ❌ 2. Ошибка: неверный chatId
# Проверяет обработку невалидного chatId
def test_get_chat_history_invalid_chat_id(api_client, api_config):
    with requests_mock.Mocker() as m:
        m.post(api_config["history_url"], status_code=400, text='{"error": "Validation failed"}')
        payload = {"chatId": "invalid_chat", "count": 10}
        response = api_client("history", payload)
        assert_validation_error(response)

# ❌ 3. Ошибка: пустой chatId
# Тестирует, что API отклоняет пустой chatId
def test_get_chat_history_empty_chat_id(api_client, api_config):
    with requests_mock.Mocker() as m:
        m.post(api_config["history_url"], status_code=400, text='{"error": "Validation failed"}')
        payload = {"chatId": "", "count": 10}
        response = api_client("history", payload)
        assert_validation_error(response)

# ❌ 4. Ошибка: некорректный count
# Проверяет обработку нечислового значения count
def test_get_chat_history_invalid_count(api_client, api_config, valid_chat_id):
    with requests_mock.Mocker() as m:
        m.post(api_config["history_url"], status_code=400, text='{"error": "Validation failed. Details: \'count\' must be a number"}')
        payload = {"chatId": valid_chat_id, "count": "invalid"}
        response = api_client("history", payload)
        assert_validation_error(response, expected_text="Validation failed. Details: 'count' must be a number")

# ❌ 5. Ошибка: неверный токен
# Проверяет, что API возвращает 401 при невалидном токене
def test_get_chat_history_invalid_token(api_client, api_config, valid_chat_id):
    invalid_url = f"https://7105.api.greenapi.com/waInstance{api_config['instance_id']}/GetChatHistory/INVALID_TOKEN"
    with requests_mock.Mocker() as m:
        m.post(invalid_url, status_code=401, text='{"error": "Unauthorized"}')
        payload = {"chatId": valid_chat_id, "count": 10}
        response = api_client("history", payload, url=invalid_url)
        assert response.status_code == 401, "Ошибка: ожидаем 401 Unauthorized"

# ❌ 6. Ошибка: таймаут запроса
# Проверяет обработку таймаута для GetChatHistory
def test_get_chat_history_timeout(api_client, api_config, valid_chat_id):
    with requests_mock.Mocker() as m:
        m.post(api_config["history_url"], exc=requests.exceptions.Timeout)
        payload = {"chatId": valid_chat_id, "count": 10}
        with pytest.raises(pytest.fail.Exception, match="API request timed out"):
            api_client("history", payload)

if __name__ == "__main__":
    pytest.main()