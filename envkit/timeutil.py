"""时区偏移与 ISO-8601 时间戳解析。"""

from __future__ import annotations


def parse_offset(text: str) -> int:
    """把 ``"+08:00"`` / ``"-05:30"`` 形式的偏移解析成**分钟数**。

    :param text: 例如 ``"+08:00"`` / ``"-05:30"`` / ``"Z"``
    :returns: 相对 UTC 的分钟数；``"Z"`` 视为 0
    :raises ValueError: 格式非法

    示例::

        >>> parse_offset("+08:00")
        480
        >>> parse_offset("-05:30")
        -330
        >>> parse_offset("Z")
        0
    """
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")

    raw = text.strip()
    if raw in ("Z", "z", "+00:00", "-00:00"):
        return 0

    body = raw.lstrip("+-")

    parts = body.split(":")
    if len(parts) != 2:
        raise ValueError(f"非法偏移：{text!r}")

    hours_text, minutes_text = parts
    if not (hours_text.isdigit() and minutes_text.isdigit()):
        raise ValueError(f"非法偏移：{text!r}")

    hours = int(hours_text)
    minutes = int(minutes_text)
    if minutes >= 60:
        raise ValueError(f"分钟数越界：{text!r}")

    return hours * 60 + minutes


def split_iso(text: str) -> dict[str, int | str]:
    """把 ISO-8601 时间戳拆成各个字段。

    返回的字典包含 ``year/month/day/hour/minute/second/offset``，
    其中 ``hour`` 是当天的 0..23 小时，``offset`` 是相对 UTC 的分钟数。

    :param text: 例如 ``"2024-03-05T08:30:00+08:00"``
    :raises ValueError: 格式非法，或时间字段越界（时 0..23、分/秒 0..59）

    示例::

        >>> split_iso("2024-03-05T08:30:00+08:00")["hour"]
        8
        >>> split_iso("2024-03-05T08:30:00+08:00")["offset"]
        480
    """
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")

    raw = text.strip()
    if "T" not in raw:
        raise ValueError(f"非法时间戳：{text!r}")

    date_part, _, rest = raw.partition("T")
    date_fields = date_part.split("-")
    if len(date_fields) != 3:
        raise ValueError(f"非法日期：{text!r}")

    year, month, day = (int(x) for x in date_fields)

    offset_part = ""
    body = rest
    if "+" in rest:
        body, _, tail = rest.partition("+")
        offset_part = "+" + tail
    elif "-" in rest:
        body, _, tail = rest.partition("-")
        offset_part = "-" + tail

    time_fields = body.split(":")
    if len(time_fields) != 3:
        raise ValueError(f"非法时间：{text!r}")

    hour_of_day, minute, second = (int(x) for x in time_fields)

    if not 0 <= hour_of_day <= 23:
        raise ValueError(f"非法时间：{text!r}")
    if not 0 <= minute <= 59:
        raise ValueError(f"非法时间：{text!r}")
    if not 0 <= second <= 59:
        raise ValueError(f"非法时间：{text!r}")

    offset = parse_offset(offset_part) if offset_part else 0

    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour_of_day,
        "minute": minute,
        "second": second,
        "offset": offset,
    }
