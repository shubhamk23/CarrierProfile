"""Unit tests for the knowledge JWT auth helpers."""

from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.knowledge.auth import (
    create_access_token,
    get_current_admin,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


class TestPasswordHashing:
    def test_round_trip(self):
        hashed = hash_password("hunter2")
        assert hashed != "hunter2"
        assert verify_password("hunter2", hashed) is True

    def test_wrong_password_rejected(self):
        hashed = hash_password("hunter2")
        assert verify_password("wrong", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        a = hash_password("same")
        b = hash_password("same")
        assert a != b   # bcrypt salts each hash
        assert verify_password("same", a)
        assert verify_password("same", b)


class TestAccessToken:
    def test_token_contains_subject(self):
        token = create_access_token({"sub": "admin"})
        decoded = jwt.decode(
            token,
            settings.knowledge_jwt_secret_key,
            algorithms=[settings.knowledge_jwt_algorithm],
        )
        assert decoded["sub"] == "admin"
        assert "exp" in decoded

    def test_token_respects_custom_expiry(self):
        token = create_access_token(
            {"sub": "admin"}, expires_delta=timedelta(seconds=1)
        )
        # Token still decodable immediately.
        decoded = jwt.decode(
            token,
            settings.knowledge_jwt_secret_key,
            algorithms=[settings.knowledge_jwt_algorithm],
        )
        assert decoded["sub"] == "admin"


class TestGetCurrentAdmin:
    @pytest.mark.asyncio
    async def test_valid_token_returns_username(self):
        token = create_access_token({"sub": "admin"})
        assert await get_current_admin(token) == "admin"

    @pytest.mark.asyncio
    async def test_missing_sub_claim_rejected(self):
        # Token signed with the right key but no `sub` claim.
        bad = jwt.encode(
            {"other": "value", "exp": 9999999999},
            settings.knowledge_jwt_secret_key,
            algorithm=settings.knowledge_jwt_algorithm,
        )
        with pytest.raises(HTTPException) as exc:
            await get_current_admin(bad)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_garbage_token_rejected(self):
        with pytest.raises(HTTPException) as exc:
            await get_current_admin("not-a-jwt")
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self):
        # Negative delta forces an immediately-expired token.
        expired = create_access_token(
            {"sub": "admin"}, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(HTTPException) as exc:
            await get_current_admin(expired)
        assert exc.value.status_code == 401
