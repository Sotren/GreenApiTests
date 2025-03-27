import pytest
import requests
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# Фикстура конфигурации
@pytest.fixture(scope="module")
def api_config():
    instance_id = os.getenv("INSTANCE_ID") or pytest.skip("INSTANCE_ID not set")
    api_token = os.getenv("API_TOKEN") or pytest.skip("API_TOKEN not set")
    base_url = "https://7105.api.greenapi.com"
    return {
        "instance_id": instance_id,
        "api_token": api_token,
        "send_url": f"{base_url}/waInstance{instance_id}/SendMessage/{api_token}",
        "history_url": f"{base_url}/waInstance{instance_id}/GetChatHistory/{api_token}"
    }

# Универсальная фикстура клиента
@pytest.fixture
def api_client(api_config):
    def _make_request(method, payload, url=None):
        if url is None:
            url = api_config[f"{method}_url"]
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            logger.info(f"Запрос ({method}): {payload}")
            logger.info(f"Ответ: {response.status_code}, {response.text}")
            return response
        except requests.exceptions.Timeout:
            pytest.fail("API request timed out")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API request failed: {e}")
    return _make_request

# Тестовые данные из .env
@pytest.fixture
def valid_chat_id():
    return os.getenv("VALID_CHAT_ID") or pytest.skip("VALID_CHAT_ID not set")

@pytest.fixture
def valid_group_id():
    return os.getenv("VALID_GROUP_ID") or pytest.skip("VALID_GROUP_ID not set")

@pytest.fixture
def valid_quoted_message_id():
    return os.getenv("VALID_QUOTED_MESSAGE_ID") or pytest.skip("VALID_QUOTED_MESSAGE_ID not set")

@pytest.fixture
def valid_message():
    return os.getenv("VALID_MESSAGE") or pytest.skip("VALID_MESSAGE not set")

# Вспомогательная функция для проверки ошибок
def assert_validation_error(response, expected_status=400, expected_text="Validation failed"):
    assert response.status_code == expected_status, f"Ошибка: ожидаем {expected_status}"
    assert expected_text in response.text, f"Ошибка: нет '{expected_text}' в ответе"