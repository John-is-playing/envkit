"""输入校验与清洗。"""

from __future__ import annotations

import re

_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# 这些名字在不同平台上代表设备或特殊目录，不能直接当文件名用
_RESERVED = {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"}


def sanitize_filename(name: str) -> str:
    """把用户输入清洗成安全的文件名。

    规则：
        * ``..`` 替换成 ``_``，防止目录穿越
        * 把路径分隔符与非法字符替换成 ``_``
        * 平台保留名（``CON`` / ``PRN`` / ``AUX`` / ``NUL`` / ``COM1`` / ``LPT1``）
          前面补一个下划线
        * 去掉首尾空白与点号

    :param name: 原始文件名
    :raises TypeError: 不是字符串
    :raises ValueError: 清洗后为空

    示例::

        >>> sanitize_filename("report<1>.txt")
        'report_1_.txt'
        >>> sanitize_filename("../../etc/passwd")
        '____etc_passwd'
        >>> sanitize_filename("CON")
        '_CON'
    """
    if not isinstance(name, str):
        raise TypeError("name 必须是字符串")

    cleaned = name.replace("..", "_")
    cleaned = _UNSAFE.sub("_", cleaned)
    cleaned = cleaned.strip(" .")

    if not cleaned:
        raise ValueError("文件名不能为空")

    stem = cleaned.split(".")[0]
    if stem.upper() in _RESERVED:
        cleaned = "_" + cleaned

    return cleaned


def parse_port(text: str | int) -> int:
    """把端口号解析成 1..65535 的整数。

    合法端口从 1 开始；0 与越界值都非法。

    :param text: 字符串或整数
    :raises ValueError: 端口非法（非数字、越界等）

    示例::

        >>> parse_port("8080")
        8080
        >>> parse_port(65535)
        65535
    """
    value = int(str(text).strip())

    if value < 1 or value > 65535:
        raise ValueError(f"非法端口：{value}")

    return value


def parse_email(text: str) -> str:
    """校验并归一化邮箱地址。

    非法输入一律抛 ``ValueError``（本库的既有契约：校验失败即抛错，
    不返回 ``None``、不返回原串）。

    :param text: 邮箱字符串
    :returns: 去掉首尾空白并小写化的邮箱
    :raises ValueError: 格式非法

    示例::

        >>> parse_email("  User@Example.COM ")
        'user@example.com'
    """
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")

    candidate = text.strip()
    if not _EMAIL.match(candidate):
        raise ValueError(f"非法邮箱：{text!r}")

    return candidate.lower()
