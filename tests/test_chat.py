import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_validation_empty_message():
    """Pesan kosong harus ditolak dengan kode status 422."""
    response = client.post("/api/v1/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_success_mocked():
    """Memastikan endpoint /api/v1/chat memproses balasan AI Groq dengan benar."""
    mock_groq_resp = {
        "id": "chatcmpl-test-123",
        "object": "chat.completion",
        "created": 1793833000,
        "model": "qwen/qwen3.8-27b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Mutasi P168L adalah mutasi emas karena menginaktivasi degron NRD proteasom 26S sehingga DREB2A menjadi stabil dan aktif secara konstitutif."
                },
                "finish_reason": "stop"
            }
        ]
    }

    class MockResponse:
        status_code = 200
        def json(self):
            return mock_groq_resp
        @property
        def text(self):
            return ""

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MockResponse()
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Kenapa P168L disebut mutasi emas?",
                "history": []
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "P168L" in data["reply"]
        assert data["model"] == "qwen/qwen3.8-27b"
        assert "Dr. Aris" in data["persona"]
