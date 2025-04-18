# --------------------------- STAGE 1: IMPORT MODULES FOR TESTING ---------------------------
import pytest
import os
import sys
from unittest.mock import patch
from llm import CustomerSupportAssistant

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --------------------------- STAGE 2: MOCK HELPERS & FIXTURES ---------------------------

@pytest.fixture
def fake_faq_data():
    return {
        "How do I check my balance?": "You can check your balance through the app dashboard.",
    }

@pytest.fixture
def assistant(tmp_path, monkeypatch, fake_faq_data):
    # Patch utils helpers
    monkeypatch.setattr("utils.load_faq_data", lambda _: fake_faq_data)
    monkeypatch.setattr("utils.find_best_faq_match", lambda question, data: data.get(question))

    history_file = tmp_path / "chat_history.json"
    return CustomerSupportAssistant(
        api_key="test-api-key",
        history_file=str(history_file),
        faq_file="tests/fake-faq.json"
    )

# --------------------------- STAGE 3: TESTS ---------------------------

# --- Input Preprocessing ---
def test_preprocess_input_trims_long_input(assistant):
    long_input = "a" * 2000
    trimmed = assistant.preprocess_input(long_input)
    assert len(trimmed) <= assistant.max_input_length

# --- FAQ Match ---
def test_get_response_faq(assistant):
    response = assistant.get_response("How do I check my balance?")
    assert response == "You can check your balance through the app dashboard."

# --- API Response ---
@patch("requests.post")
def test_get_response_from_llm(mock_post, assistant):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": "This is a reply from the model."}}]
    }

    response = assistant.get_response("What's my last transaction?")
    assert response == "This is a reply from the model."

# --- API Error Handling ---
@patch("requests.post", side_effect=Exception("API Failure"))
def test_get_response_with_api_error(mock_post, assistant):
    response = assistant.get_response("What is my balance?")
    assert "couldn't reach the server" in response.lower()

# --- Clear Chat History ---
def test_clear_history(assistant):
    assistant.chat_history.append({"role": "user", "content": "Test"})
    assistant.clear_history()
    assert assistant.chat_history == []

# --- Load from Empty File ---
def test_load_history_from_empty_file(tmp_path):
    empty_history_file = tmp_path / "empty_history.json"
    empty_history_file.write_text("")
    assistant = CustomerSupportAssistant(
        api_key="test-key",
        history_file=str(empty_history_file)
    )
    assert assistant.chat_history == []
