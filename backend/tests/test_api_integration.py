import pytest
from app.main import app


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "testpass123"},
    )
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 409


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "testpass123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "noone@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_get_me_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 403


def test_get_me_authenticated(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "testpass123"},
    ).json()
    token = reg["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"
