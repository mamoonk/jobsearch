from app.middleware.auth import hash_password, verify_password


def test_password_hashing():
    hashed = hash_password("testpass123")
    assert verify_password("testpass123", hashed)
    assert not verify_password("wrongpass", hashed)
