"""组件注册表。"""

from __future__ import annotations

import pytest

from envkit import Registry


def test_register_and_count():
    reg = Registry()
    reg.register("a", lambda: 1)
    reg.register("b", lambda: 2)
    assert len(reg) == 2


def test_has():
    reg = Registry()
    reg.register("a", lambda: 1)
    assert reg.has("a") is True
    assert reg.has("missing") is False


def test_resolve_builds_lazily():
    calls = []

    def factory():
        calls.append(1)
        return {"built": len(calls)}

    reg = Registry()
    reg.register("thing", factory)
    assert calls == []
    first = reg.resolve("thing")
    assert calls == [1]
    assert first == {"built": 1}


def test_resolve_caches_instance():
    calls = []
    reg = Registry()
    reg.register("thing", lambda: calls.append(1) or object())
    a = reg.resolve("thing")
    b = reg.resolve("thing")
    assert a is b
    assert len(calls) == 1


def test_resolve_passes_kwargs_on_first_build():
    reg = Registry()
    reg.register("point", lambda x, y: (x, y))
    assert reg.resolve("point", x=1, y=2) == (1, 2)


def test_resolve_rebuilds_when_kwargs_change():
    reg = Registry()
    reg.register("conn", lambda host="localhost": {"host": host})

    first = reg.resolve("conn", host="db1")
    second = reg.resolve("conn", host="db2")

    assert first["host"] == "db1"
    assert second["host"] == "db2"
    assert second is not first


def test_resolve_unknown_raises():
    reg = Registry()
    with pytest.raises(KeyError):
        reg.resolve("nope")


def test_register_empty_key_rejected():
    reg = Registry()
    with pytest.raises(ValueError):
        reg.register("", lambda: 1)


def test_register_non_callable_rejected():
    reg = Registry()
    with pytest.raises(TypeError):
        reg.register("a", 123)  # type: ignore[arg-type]


def test_register_duplicate_rejected():
    reg = Registry()
    reg.register("a", lambda: 1)
    with pytest.raises(KeyError):
        reg.register("a", lambda: 2)


def test_clear_drops_instances_but_keeps_registration():
    reg = Registry()
    reg.register("a", lambda: object())
    reg.resolve("a")
    reg.clear()
    assert reg.has("a") is True
    assert reg.snapshot() == {}
