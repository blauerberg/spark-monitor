import pytest

from spark_monitor.main import DisplayMode, _make_parser


def test_default_is_full():
    args = _make_parser().parse_args([])
    assert not args.compact_vertical
    assert not args.compact_horizontal


def test_compact_vertical_flag():
    args = _make_parser().parse_args(["--compact-vertical"])
    assert args.compact_vertical
    assert not args.compact_horizontal


def test_compact_horizontal_flag():
    args = _make_parser().parse_args(["--compact-horizontal"])
    assert not args.compact_vertical
    assert args.compact_horizontal


def test_mutual_exclusion_raises():
    with pytest.raises(SystemExit):
        _make_parser().parse_args(["--compact-vertical", "--compact-horizontal"])


def test_compact_flag_removed():
    with pytest.raises(SystemExit):
        _make_parser().parse_args(["--compact"])


def test_statusline_flag():
    args = _make_parser().parse_args(["--statusline"])
    assert args.statusline
    assert not args.compact_vertical
    assert not args.compact_horizontal


def test_statusline_mutually_exclusive():
    with pytest.raises(SystemExit):
        _make_parser().parse_args(["--statusline", "--compact-vertical"])


def test_display_mode_enum_values():
    assert DisplayMode.FULL.value == "full"
    assert DisplayMode.VERTICAL.value == "vertical"
    assert DisplayMode.HORIZONTAL.value == "horizontal"
    assert DisplayMode.STATUSLINE.value == "statusline"
