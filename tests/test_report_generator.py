#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开题报告直出器（report_generator）自测。
测试五大模块生成、模板占位符填充、文件写入与标准化输出。
"""

import sys
import os

# 将 core/scripts/ 加入 sys.path 以便直接导入脚本模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "scripts"))

from report_generator import generate_report


# ========== 公共测试数据 ==========

SAMPLE_PROPOSAL = {
    "title": "医疗大模型的科室问询微调",
    "degree": "master",
    "problem_awareness": "通用大模型在医疗问询场景精度不足，缺乏科室特异性。",
    "research_significance": "通过科室级微调提升医疗大模型问询精度，兼具理论与实际价值。",
    "differentiation": "聚焦单一科室微调，区别于通用大模型的全场景覆盖。",
    "research_content": "1. 调研医疗大模型现状；2. 设计科室微调方案；3. 实验验证。",
    "literature_review_outline": "梳理医疗大模型与微调技术研究，规划文献不少于30篇。"
}


def test_five_modules():
    """测试生成五大模块（选题依据/研究现状/研究内容/研究方案/进度安排）"""
    result = generate_report(SAMPLE_PROPOSAL)
    assert result["status"] == "success"
    md = result["data"]["report_markdown"]
    # 五大模块关键词
    assert "选题依据" in md
    assert "研究现状" in md
    assert "研究内容" in md
    assert "研究方案" in md
    assert "进度安排" in md


def test_template_filling():
    """测试模板占位符填充"""
    result = generate_report(SAMPLE_PROPOSAL)
    assert result["status"] == "success"
    md = result["data"]["report_markdown"]
    # 不应残留未填充的占位符 {{...}}
    assert "{{" not in md
    assert "}}" not in md
    # 应包含提案标题
    assert SAMPLE_PROPOSAL["title"] in md


def test_output_to_file():
    """测试写入 output/ 目录"""
    result = generate_report(SAMPLE_PROPOSAL)
    assert result["status"] == "success"
    report_path = result["data"]["report_path"]
    # 路径应包含 output 目录
    assert "output" in report_path
    # 文件应实际存在
    assert os.path.exists(report_path)
    # 文件应为 .md 后缀
    assert report_path.endswith(".md")


def test_standard_output():
    """测试返回 dict 含 status/data"""
    result = generate_report(SAMPLE_PROPOSAL)
    assert isinstance(result, dict)
    assert "status" in result
    assert "data" in result
    assert result["status"] == "success"
    # data 应含 report_markdown 与 report_path
    assert "report_markdown" in result["data"]
    assert "report_path" in result["data"]
