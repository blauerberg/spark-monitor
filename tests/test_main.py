import pytest

from spark_monitor.main import DisplayMode, _make_parser


def test_default_is_full():
    args = _make_parser().parse_args([])
    assert not args.statusline


def test_statusline_flag():
    args = _make_parser().parse_args(["--statusline"])
    assert args.statusline


def test_display_mode_enum_values():
    assert DisplayMode.FULL.value == "full"
    assert DisplayMode.STATUSLINE.value == "statusline"
