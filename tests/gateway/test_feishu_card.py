"""Tests for gateway.platforms.feishu_card."""
from __future__ import annotations
import pytest
from gateway.platforms.feishu_card import format_token_count

class TestFormatTokenCount:
    @pytest.mark.parametrize(
        "value, expected",
        [
            (0, "0"),
            (48, "48"),
            (999, "999"),
            (1000, "1.0k"),
            (1100, "1.1k"),
            (11100, "11.1k"),
            (999999, "1000.0k"),
            (1000000, "1.0M"),
            (3400000, "3.4M"),
        ],
    )
    def test_format_token_count(self, value, expected):
        assert format_token_count(value) == expected

    def test_format_token_count_negative_returns_zero(self):
        assert format_token_count(-5) == "0"


from gateway.platforms.feishu_card import get_tool_display

class TestGetToolDisplay:
    @pytest.mark.parametrize(
        "tool_name, expected",
        [
            ("Read", "Read · 阅读文件"),
            ("read_file", "Read · 阅读文件"),
            ("Bash", "Bash · 执行命令"),
            ("terminal", "Bash · 执行命令"),
            ("Edit", "Edit · 改代码"),
            ("edit_file", "Edit · 改代码"),
            ("Write", "Write · 写文件"),
            ("write_file", "Write · 写文件"),
            ("MultiEdit", "MultiEdit · 批量改代码"),
            ("Grep", "Grep · 搜索代码"),
            ("Glob", "Glob · 查找文件"),
            ("WebFetch", "WebFetch · 抓取网页"),
            ("web_fetch", "WebFetch · 抓取网页"),
            ("WebSearch", "WebSearch · 搜索网络"),
            ("web_search", "WebSearch · 搜索网络"),
            ("Task", "Agent · 派出子任务"),
            ("Agent", "Agent · 派出子任务"),
            ("TodoWrite", "TodoWrite · 更新任务"),
            ("unknown_tool_xyz", "unknown_tool_xyz"),
        ],
    )
    def test_get_tool_display(self, tool_name, expected):
        assert get_tool_display(tool_name) == expected


from gateway.platforms.feishu_card import parse_markdown_tables

class TestParseMarkdownTables:
    def test_no_table_returns_single_text(self):
        result = parse_markdown_tables("just some text")
        assert result == [("text", "just some text")]

    def test_simple_table(self):
        md = "before\n\n| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n\nafter"
        result = parse_markdown_tables(md)
        assert len(result) == 3
        assert result[0] == ("text", "before")
        assert result[1][0] == "table"
        table = result[1][1]
        assert table["columns"] == [
            {"name": "col_0", "display_name": "A"},
            {"name": "col_1", "display_name": "B"},
        ]
        assert table["rows"] == [
            {"col_0": "1", "col_1": "2"},
            {"col_0": "3", "col_1": "4"},
        ]
        assert result[2] == ("text", "after")

    def test_empty_input(self):
        result = parse_markdown_tables("")
        assert result == [("text", "")]

    def test_table_only(self):
        md = "| X |\n|---|\n| 1 |"
        result = parse_markdown_tables(md)
        assert len(result) == 1
        assert result[0][0] == "table"

    def test_multiple_tables(self):
        md = "| A |\n|---|\n| 1 |\n\nmiddle\n\n| B |\n|---|\n| 2 |"
        result = parse_markdown_tables(md)
        assert len(result) == 3
        assert result[0][0] == "table"
        assert result[1] == ("text", "middle")
        assert result[2][0] == "table"
