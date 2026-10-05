"""容量字符串解析与格式化。"""

from __future__ import annotations

_UNIT_FACTORS = {
    "B": 1,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "TB": 1000**4,
}

_UNIT_ALIASES = {
    "K": "KB",
    "M": "MB",
    "G": "GB",
    "T": "TB",
}


def parse_size(text: str) -> int:
    """把容量字符串解析成字节数（十进制单位，1 KB = 1000 B）。

    支持带空格与不带空格两种写法，单位大小写不敏感：

    :param text: 例如 ``"1.5 MB"`` / ``"512KB"`` / ``"2 GB"`` / ``"4096"``
    :returns: 字节数（整数）
    :raises ValueError: 空字符串、未知单位或数字部分无法解析

    示例::

        >>> parse_size("1.5 MB")
        1500000
        >>> parse_size("512KB")
        512000
        >>> parse_size("4096")
        4096
    """
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")

    raw = text.strip().upper()
    if not raw:
        raise ValueError("容量字符串不能为空")

    number, _, unit = raw.partition(" ")
    unit = unit.strip() or "B"
    unit = _UNIT_ALIASES.get(unit, unit)
    if unit not in _UNIT_FACTORS:
        raise ValueError(f"未知容量单位：{unit!r}")

    return int(float(number) * _UNIT_FACTORS[unit])


def format_size(num_bytes: int, *, unit: str = "MB") -> str:
    """把字节数换算成指定单位并保留两位小数。

    :param num_bytes: 字节数，必须非负
    :param unit: 目标单位，取值 ``B/ KB/ MB/ GB/ TB``
    :returns: 例如 ``1572864`` → ``"1.50 MB"``

    示例::

        >>> format_size(1500000)
        '1.50 MB'
        >>> format_size(512000, unit="KB")
        '512.00 KB'
    """
    if num_bytes < 0:
        raise ValueError("num_bytes 不能为负数")

    factor = _UNIT_FACTORS.get(unit.upper())
    if factor is None:
        raise ValueError(f"未知容量单位：{unit!r}")

    return f"{num_bytes / factor:.1f} {unit.upper()}"
