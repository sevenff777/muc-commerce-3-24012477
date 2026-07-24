import sys
from pathlib import Path

# 将项目的根目录加入到 Python 搜索路径中，避免测试时报 "ModuleNotFoundError: No module named 'app'"
root_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_path))

import pytest
from app import app


@pytest.fixture
def client():
    """创建 Flask 测试客户端，并开启测试模式"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def login(client, username="student", password="day07"):
    """辅助函数：模拟登录"""
    return client.post("/login", data={"username": username, "password": password})


def test_metrics_api_unauthenticated(client):
    """未登录时访问 /api/metrics 应重定向到登录页"""
    resp = client.get("/api/metrics")
    assert resp.status_code == 302
    assert resp.location.endswith("/login")


def test_metrics_api_authenticated(client):
    """登录后访问 /api/metrics 应返回正确的指标数据"""
    login(client)
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    metrics = data["metrics"]
    assert isinstance(metrics, list)
    # 至少有一个指标，且每个指标包含 label, value, note
    if metrics:
        for m in metrics:
            assert "label" in m
            assert "value" in m
            assert "note" in m


def test_categories_api_authenticated_no_filter(client):
    """登录后访问 /api/categories（不带参数）应返回全部类别数据"""
    login(client)
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["category"] == "全部"
    rows = data["rows"]
    assert isinstance(rows, list)


def test_categories_api_authenticated_with_filter(client):
    """登录后访问 /api/categories?category=Fashion 应返回筛选后的数据"""
    login(client)
    category = "Fashion"
    resp = client.get(f"/api/categories?category={category}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["category"] == category
    rows = data["rows"]
    for row in rows:
        assert row.get("偏好品类") == category


def test_health_endpoint(client):
    """/health 不需要登录，返回服务状态"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["service"] == "day08-flask-upgrade"