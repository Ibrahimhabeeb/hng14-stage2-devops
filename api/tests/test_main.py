import importlib
import os
import sys
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient


API_DIR = Path(__file__).resolve().parent.parent
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def _load_module_with_mocked_redis(mock_redis):
    os.environ["REDIS_HOST"] = "redis"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_PASSWORD"] = ""
    import main as main_module

    importlib.reload(main_module)
    main_module.r = mock_redis
    return main_module


def test_create_job_pushes_to_queue_and_sets_queued_status():
    fake_redis = Mock()
    module = _load_module_with_mocked_redis(fake_redis)
    client = TestClient(module.app)

    response = client.post("/jobs")

    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    fake_redis.lpush.assert_called_once_with("job", body["job_id"])
    fake_redis.hset.assert_called_once_with(f"job:{body['job_id']}", "status", "queued")


def test_get_job_returns_status_when_present():
    fake_redis = Mock()
    fake_redis.hget.return_value = "completed"
    module = _load_module_with_mocked_redis(fake_redis)
    client = TestClient(module.app)

    response = client.get("/jobs/job-123")

    assert response.status_code == 200
    assert response.json() == {"job_id": "job-123", "status": "completed"}


def test_get_job_returns_not_found_when_missing():
    fake_redis = Mock()
    fake_redis.hget.return_value = None
    module = _load_module_with_mocked_redis(fake_redis)
    client = TestClient(module.app)

    response = client.get("/jobs/missing-job")

    assert response.status_code == 200
    assert response.json() == {"error": "not found"}


def test_health_uses_redis_ping():
    fake_redis = Mock()
    module = _load_module_with_mocked_redis(fake_redis)
    client = TestClient(module.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    fake_redis.ping.assert_called_once()
