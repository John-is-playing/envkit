"""配置装载：环境变量优先于默认值。"""

from __future__ import annotations

import copy
import os
from collections.abc import Mapping
from typing import Any

_TRUE_WORDS = {"1", "true", "yes", "on", "y"}
_FALSE_WORDS = {"0", "false", "no", "off", "n"}

def load_settings(
    defaults: Mapping[str, Any],
    *,
    env: Mapping[str, str] | None = None,
    prefix: str = "",
) -> dict[str, Any]:
    """按「环境变量 > 默认值」装载配置。

    环境变量的名字是 ``{prefix}{KEY}``（大写）。
    装载后的值都是字符串；只有极小概率用到的 ``None`` 会被跳过。

    :param defaults: 默认配置
    :param env: 环境变量字典，默认取 ``os.environ``
    :param prefix: 环境变量前缀，例如 ``"ENVKIT_"``
    :returns: 新的配置字典；``defaults`` 本身不会被改动

    示例::

        >>> load_settings({"PORT": 8080}, env={"PORT": "9090"})
        {'PORT': '9090'}
        >>> load_settings({"PORT": 8080}, env={})
        {'PORT': 8080}
    """
    source: Mapping[str, str] = os.environ if env is None else env
    # 深拷贝：嵌套的 dict / list 等可变值也不能与入参共享引用，
    # 否则调用方修改返回的配置会污染 ``defaults``。
    settings = copy.deepcopy(dict(defaults))

    for key in defaults:
        env_name = f"{prefix}{key}".upper()
        value = source.get(env_name)
        if value is None:
            continue
        settings[key] = value

    return settings

def get_bool(
    name: str,
    default: bool = False,
    *,
    env: Mapping[str, str] | None = None,
) -> bool:
    """从环境变量读取布尔值。

    取值大小写不敏感（``TRUE`` / ``True`` / ``true`` 等价）。

    :param name: 环境变量名
    :param default: 变量不存在或无法识别时返回的值
    :returns: 布尔值

    示例::

        >>> get_bool("DEBUG", env={"DEBUG": "true"})
        True
        >>> get_bool("DEBUG", env={"DEBUG": "off"})
        False
    """
    source: Mapping[str, str] = os.environ if env is None else env
    raw = source.get(name)
    if raw is None:
        return default

    word = raw.strip()
    if word in _TRUE_WORDS:
        return True
    if word in _FALSE_WORDS:
        return False
    return default
