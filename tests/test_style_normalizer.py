#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术风格中性化处理器（style_normalizer）自测。
测试词频替换、句首禁用词过滤、主动被动态互换、高重复风险段落检测、
空输入处理与标准化输出。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from style_normalizer import remove_ai_traces


def test_replace_ai_phrases():
    """测试 AI 化术语被替换为学术中性表达"""
    text = (
        "本方法显著提升了系统性能，大幅提高了准确率，"
        "充分证明了模型的有效性。"
    )
    result = remove_ai_traces(text)
    assert result["status"] == "success"
    normalized = result["data"]["normalized_text"]
    # "显著提升" 应被替换为 "呈现正向关联"
    assert "显著提升" not in normalized
    assert "呈现正向关联" in normalized
    # "大幅提高" 应被替换为 "有所提升"
    assert "大幅提高" not in normalized
    assert "有所提升" in normalized
    # 替换次数应大于 0
    assert result["data"]["replacements_count"] > 0


def test_filter_sentence_start():
    """测试句首禁用词被移除"""
    text = (
        "首先，我们调研了相关文献。"
        "其次，设计了实验方案。"
        "最后，验证了方法有效性。"
        "综上所述，本研究具备理论价值。"
    )
    result = remove_ai_traces(text)
    assert result["status"] == "success"
    normalized = result["data"]["normalized_text"]
    # 句首禁用词 "首先/其次/最后" 应被移除，"综上所述" 应被替换
    assert "首先" not in normalized
    assert "其次" not in normalized
    assert "最后" not in normalized
    assert "综上所述" not in normalized


def test_swap_voice():
    """测试主动语态转为中性表达"""
    text = (
        "我们提出了一种新的微调方法。"
        "本文设计了一个高效的模型架构。"
    )
    result = remove_ai_traces(text)
    assert result["status"] == "success"
    normalized = result["data"]["normalized_text"]
    # "我们提出" 应转为 "本研究提出"
    assert "我们提出" not in normalized
    assert "本研究提出" in normalized
    # "本文设计" 应转为 "本研究设计"
    assert "本文设计" not in normalized
    assert "本研究设计" in normalized


def test_high_risk_detection():
    """测试高重复风险段落检测（短段落 + 列举式标记）"""
    text = (
        "1. 调研现状。\n"
        "2. 设计方案。\n"
        "3. 实验验证。"
    )
    result = remove_ai_traces(text)
    assert result["status"] == "success"
    high_risk_sections = result["data"]["high_risk_sections"]
    # 应检测到高重复风险段落
    assert isinstance(high_risk_sections, list)
    assert len(high_risk_sections) > 0


def test_empty_input():
    """测试空输入或 None 返回 status=error"""
    # 空字符串
    result_empty = remove_ai_traces("")
    assert result_empty["status"] == "error"
    assert result_empty["data"] is None
    assert result_empty["error_message"] is not None
    # None 输入
    result_none = remove_ai_traces(None)
    assert result_none["status"] == "error"
    assert result_none["data"] is None
    assert result_none["error_message"] is not None


def test_standard_output():
    """测试返回 dict 含 status/data/error_message 三字段"""
    result = remove_ai_traces("这是一段普通的学术文本，用于验证输出结构。")
    assert isinstance(result, dict)
    assert "status" in result
    assert "data" in result
    assert "error_message" in result
    assert result["status"] == "success"
    # data 应含 normalized_text、replacements_count、high_risk_sections
    assert "normalized_text" in result["data"]
    assert "replacements_count" in result["data"]
    assert "high_risk_sections" in result["data"]
