"""按需构建的组件注册表。"""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any


class Registry:
    """把「键 → 构建工厂」登记起来，首次解析时才真正构建。

    同一个键解析出的实例会被缓存：再次 ``resolve`` 时复用，
    因此组件在整个进程内是单例的。

    示例::

        >>> reg = Registry()
        >>> reg.register("counter", lambda: 0)
        >>> reg.resolve("counter")
        0
    """

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., Any]] = {}
        self._instances: dict[str, Any] = {}

    def register(self, key: str, factory: Callable[..., Any]) -> "Registry":
        """登记 ``key`` 的构建工厂；重复登记会报错。"""
        if not key:
            raise ValueError("key 不能为空")
        if not callable(factory):
            raise TypeError("factory 必须是可调用对象")
        if key in self._factories:
            raise KeyError(f"已注册：{key!r}")
        self._factories[key] = factory
        return self

    def has(self, key: str) -> bool:
        """``key`` 是否已登记（不含仅解析过但未登记的）。"""
        return key in self._factories

    def resolve(self, key: str, **kwargs: Any) -> Any:
        """解析 ``key`` 对应的实例。

        首次解析会用 ``kwargs`` 调用工厂并缓存结果；再次解析同一键时，
        若传入的参数与首次不同，应重新构建并替换缓存。

        :raises KeyError: ``key`` 未登记
        """
        if key not in self._factories:
            raise KeyError(f"未注册：{key!r}")

        if key in self._instances:
            return self._instances[key]

        instance = self._factories[key](**kwargs)
        self._instances[key] = instance
        return instance

    def snapshot(self) -> dict[str, Any]:
        """返回当前已解析实例的只读快照。

        调用方拿到的是快照，对它的任何改动都不应影响注册表本身。
        """
        return copy.deepcopy(self._instances)

    def clear(self) -> None:
        """丢弃所有已解析实例（保留登记信息）。"""
        self._instances.clear()

    def __len__(self) -> int:
        return len(self._factories)
