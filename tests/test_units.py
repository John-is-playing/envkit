"""容量解析与格式化。"""

from __future__ import annotations

import pytest

from envkit import format_size, parse_size


def test_parse_plain_bytes():
    assert parse_size("4096") == 4096
    assert parse_size("0") == 0


def test_parse_kb():
    assert parse_size("512 KB") == 512_000
    assert parse_size("1 KB") == 1000


def test_parse_mb_with_decimal():
    assert parse_size("1.5 MB") == 1_500_000
    assert parse_size("0.5 MB") == 500_000


def test_parse_gb_and_tb():
    assert parse_size("2 GB") == 2_000_000_000
    assert parse_size("1 TB") == 1_000_000_000_000


def test_parse_is_case_insensitive():
    assert parse_size("3 MB") == 3_000_000
    assert parse_size("3 mb") == 3_000_000
    assert parse_size("3 Mb") == 3_000_000


def test_parse_trims_whitespace():
    assert parse_size("  1 GB  ") == 1_000_000_000


def test_parse_single_letter_aliases():
    assert parse_size("2 G") == 2_000_000_000
    assert parse_size("7 M") == 7_000_000


def test_parse_without_space():
    assert parse_size("512KB") == 512_000
    assert parse_size("1.5GB") == 1_500_000_000
    assert parse_size("2TB") == 2_000_000_000_000
    assert parse_size("3B") == 3


def test_parse_rejects_empty():
    with pytest.raises(ValueError):
        parse_size("   ")


def test_parse_rejects_unknown_unit():
    with pytest.raises(ValueError):
        parse_size("5 XB")


def test_parse_rejects_non_str():
    with pytest.raises(TypeError):
        parse_size(512)  # type: ignore[arg-type]


def test_format_basic():
    assert format_size(1_500_000) == "1.50 MB"


def test_format_other_units():
    assert format_size(512_000, unit="KB") == "512.00 KB"
    assert format_size(2_000_000_000, unit="GB") == "2.00 GB"


def test_format_zero():
    assert format_size(0) == "0.00 MB"


def test_format_rejects_negative():
    with pytest.raises(ValueError):
        format_size(-1)


def test_format_rejects_unknown_unit():
    with pytest.raises(ValueError):
        format_size(100, unit="XB")
