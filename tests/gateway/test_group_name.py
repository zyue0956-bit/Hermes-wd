"""Tests for gateway.platforms.group_name — extraction + rate limiter."""
import pytest
from gateway.platforms.group_name import extract_group_name, GroupNameRateLimiter


class TestExtractGroupName:
    def test_single_tag(self):
        text = "你好！<group-name>修复群聊功能</group-name>我来帮你处理。"
        clean, name = extract_group_name(text)
        assert name == "修复群聊功能"
        assert "<group-name>" not in clean
        assert "你好！" in clean
        assert "我来帮你处理。" in clean

    def test_no_tag(self):
        clean, name = extract_group_name("普通回复内容")
        assert name is None
        assert clean == "普通回复内容"

    def test_empty_tag(self):
        clean, name = extract_group_name("text<group-name></group-name>more")
        assert name is None

    def test_truncate_to_20(self):
        long_name = "这是一个超过二十个字符的非常长的群名称测试用例"
        text = f"<group-name>{long_name}</group-name>内容"
        _, name = extract_group_name(text)
        assert name is not None
        assert len(name) <= 20

    def test_multiple_tags_takes_first(self):
        text = "<group-name>第一个</group-name>中间<group-name>第二个</group-name>"
        clean, name = extract_group_name(text)
        assert name == "第一个"
        assert "<group-name>" not in clean

    def test_whitespace_stripped(self):
        text = "<group-name>  任务名  </group-name>"
        _, name = extract_group_name(text)
        assert name == "任务名"


class TestGroupNameRateLimiter:
    def test_first_update_allowed(self):
        limiter = GroupNameRateLimiter(interval_seconds=300)
        assert limiter.should_update("chat_1") is True

    def test_second_update_within_interval_blocked(self):
        limiter = GroupNameRateLimiter(interval_seconds=300)
        limiter.record_update("chat_1")
        assert limiter.should_update("chat_1") is False

    def test_different_chats_independent(self):
        limiter = GroupNameRateLimiter(interval_seconds=300)
        limiter.record_update("chat_1")
        assert limiter.should_update("chat_2") is True
