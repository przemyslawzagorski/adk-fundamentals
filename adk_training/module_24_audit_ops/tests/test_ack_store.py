"""Tests for SQLite ack store."""
import time

from adk_training.module_24_audit_ops.ack_store import AckStore
from adk_training.module_24_audit_ops.safety import DisclaimerAck


def _ack(host="example.test"):
    return DisclaimerAck(
        acknowledged=True,
        user_id="u",
        target_url=f"https://{host}/",
        timestamp=time.time(),
    )


def test_register_and_get_roundtrip(tmp_path):
    s = AckStore(tmp_path / "acks.db")
    token = s.register(_ack())
    got = s.get(token)
    assert got is not None
    assert got.user_id == "u"
    assert "example.test" in got.target_url


def test_unknown_token_returns_none(tmp_path):
    s = AckStore(tmp_path / "acks.db")
    assert s.get("does-not-exist") is None
    assert s.get("") is None
    assert s.get(None) is None  # type: ignore[arg-type]


def test_expired_token_is_purged(tmp_path):
    s = AckStore(tmp_path / "acks.db", default_ttl_s=0)
    token = s.register(_ack(), ttl_s=0)
    time.sleep(0.05)
    assert s.get(token) is None


def test_revoke(tmp_path):
    s = AckStore(tmp_path / "acks.db")
    token = s.register(_ack())
    assert s.revoke(token) is True
    assert s.get(token) is None
    assert s.revoke(token) is False


def test_persists_across_instances(tmp_path):
    db = tmp_path / "acks.db"
    s1 = AckStore(db)
    token = s1.register(_ack(), ttl_s=600)
    s2 = AckStore(db)
    assert s2.get(token) is not None
